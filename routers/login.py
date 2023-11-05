# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter
from pydantic import BaseModel
import string
import random
import hashlib
from sqlalchemy import select
from sqlalchemy.orm import Session

import config

from models import ENGINE, get_table
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
    with Session(ENGINE) as session:
        user_table = get_table("users")
        if user_table is None:
            return {
                "error": "internal server error",
            }
        stmt = select(user_table.c.password_salt, user_table.c.password_hash).where(user_table.c.email == req.email)
        rows = session.execute(stmt).fetchall()
        for row in rows:
            salt = row[0]
            password_bytes = ''.join([req.password, salt]).encode()
            h = hashlib.sha256(password_bytes).hexdigest()
            if h != row[1]:
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