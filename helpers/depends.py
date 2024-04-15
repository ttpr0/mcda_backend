# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from typing import Annotated, Any
from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

import config

def decode_token(token: str) -> Any:
    try:
        payload = jwt.decode(token, config.JWT_KEY, algorithms=[config.JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
    if datetime.fromtimestamp(payload["exp"]) < datetime.now():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})
    return payload["sub"]

class User:
    name: str
    group: str

    def __init__(self, name: str, group: str):
        self.name = name
        self.group = group
    
    def get_name(self):
        return self.name
    def get_group(self):
        return self.group


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="",
    scheme_name="JWT",
)

async def get_current_user(token: Annotated[str, Depends(reuseable_oauth)]) -> User:
    subject = decode_token(token)
    return User(subject["id"], subject["group"])
