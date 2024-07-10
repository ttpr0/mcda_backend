# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""Session state manager
"""

from __future__ import annotations

import string
import random
from datetime import datetime, timedelta
from typing import Any
import asyncio


def _generate_session_id() -> str:
    letters = string.ascii_lowercase
    sid = ''.join(random.choice(letters) for i in range(10))
    return sid

class Session:
    """Session object to interact with session data.

    Note:
        - in future this might be replaced by a proper session db (e.g. redis)
    """
    _data: dict[str, Any]
    def __init__(self, data: dict[str, Any]):
        self._data = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]
    
    def __setitem__(self, key: str, value: Any):
        self._data[key] = value

    def commit(self):
        pass

class SessionStorage:
    """Session storage class.
    """
    _sessions: dict[tuple[str, str], tuple[datetime, dict[str, Any]]]

    def __init__(self):
        self._sessions = {}

    def periodically_clear(self, iter_seconds: int, timeout_minutes):
        asyncio.create_task(self._clear_outdated_sessions(iter_seconds, timeout_minutes))

    async def _clear_outdated_sessions(self, iter_seconds: int, timeout_minutes: int):
        while True:
            now = datetime.now()
            to_be_deleted = []
            for user, session_id in self._sessions:
                time, _ = self._sessions[(user, session_id)]
                if now - time > timedelta(minutes=timeout_minutes):
                    to_be_deleted.append((user, session_id))
            for key in to_be_deleted:
                del self._sessions[key]
            await asyncio.sleep(iter_seconds)

    def new_session(self, user: str) -> str:
        """Creates a new session and returns the session id
        """
        while True:
            session_id = _generate_session_id()
            if (user, session_id) not in self._sessions:
                now = datetime.now()
                self._sessions[(user, session_id)] = (now, {})
                return session_id

    def has_session(self, user: str, session_id: str) -> bool:
        return (user, session_id) in self._sessions

    def get_session(self, user: str, session_id: str) -> Session:
        """Returns the session object
        """
        if (user, session_id) not in self._sessions:
            raise Exception("Session not found")
        _, session = self._sessions[(user, session_id)]
        self._sessions[(user, session_id)] = (datetime.now(), session)
        return Session(session)

    def remove_session(self, user: str, session_id: str):
        if (user, session_id) not in self._sessions:
            raise Exception("Session not found")
        del self._sessions[(user, session_id)]

STATE = None

def init_state():
    """Initializes the session state.
    """
    global STATE
    STATE = SessionStorage()
    STATE.periodically_clear(60 * 60, 24 * 60)

def get_state() -> SessionStorage:
    """Returns the session state singleton.

    Note:
        - This can be used as a fastapi dependency
    """
    global STATE
    if STATE is None:
        raise ValueError("This should not have happened.")
    return STATE
