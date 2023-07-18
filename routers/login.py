# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter
from pydantic import BaseModel
import string
import random
import hashlib
from sqlalchemy.orm import Session

import config

from models import engine, User
from state import USER_SESSIONS


def generate_session_key() -> str:
    letters = string.ascii_lowercase
    key = ''.join(random.choice(letters) for i in range(20))
    return key


router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login_api(req: LoginRequest):
    with Session(engine) as session:
        rows = session.query(User).where(User.email == req.email)
        for row in rows:
            salt = row.password_salt
            password_bytes = ''.join([req.password, salt]).encode()
            h = hashlib.sha256(password_bytes).hexdigest()
            if h != row.password_hash:
                return {
                    "error": "wrong password",
                }
            else:
                key = generate_session_key()
                USER_SESSIONS.add(key)
                return {
                    "session_key" : key
                }
        return {
            "error": "email not found",
        }
    
class LogoutRequest(BaseModel):
    session_key: str

@router.post("/logout")
async def logout_api(req: LogoutRequest):
    if req.session_key in USER_SESSIONS:
        USER_SESSIONS.remove(req.session_key)
    print(req.session_key)
    return {}