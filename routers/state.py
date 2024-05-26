# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

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

class SessionStorage:
    _sessions: dict[tuple[str, str], tuple[datetime, Any]]

    def __init__(self):
        self._sessions = {}

    def periodically_clear(self, iter_seconds: int, timeout_minutes):
        asyncio.create_task(self._clear_outdated_sessions(iter_seconds, timeout_minutes))

    async def _clear_outdated_sessions(self, iter_seconds: int, timeout_minutes: int):
        while True:
            now = datetime.now()
            for user, session_id in self._sessions:
                time, _ = self._sessions[(user, session_id)]
                if now - time > timedelta(minutes=timeout_minutes):
                    del self._sessions[(user, session_id)]
            await asyncio.sleep(iter_seconds)

    def new_session(self, user: str) -> str:
        """Creates a new session and returns the session id
        """
        while True:
            session_id = _generate_session_id()
            if (user, session_id) not in self._sessions:
                now = datetime.now()
                self._sessions[(user, session_id)] = (now, None)
                return session_id

    def has_session(self, user: str, session_id: str) -> bool:
        return (user, session_id) in self._sessions

    def set_session(self, user: str, session_id: str, value: Any) -> None:
        """Returns the session object
        """
        if (user, session_id) not in self._sessions:
            raise Exception("Session not found")
        self._sessions[(user, session_id)] = (datetime.now(), value)

    def get_session(self, user: str, session_id: str) -> Any:
        """Returns the session object
        """
        if (user, session_id) not in self._sessions:
            raise Exception("Session not found")
        _, session = self._sessions[(user, session_id)]
        self._sessions[(user, session_id)] = (datetime.now(), session)
        return session

    def remove_session(self, user: str, session_id: str):
        if (user, session_id) not in self._sessions:
            raise Exception("Session not found")
        del self._sessions[(user, session_id)]

STATE = SessionStorage()

def get_state() -> SessionStorage:
    global STATE
    return STATE
