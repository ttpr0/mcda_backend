# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import create_engine, Column, Integer, String
from geoalchemy2 import Geometry
from sqlalchemy.orm import Session, declarative_base
from shapely import Point, Polygon

# from . import Base

# class User(Base):
#     __tablename__ = "users"

#     pid = Column("pid", Integer, primary_key=True, autoincrement=True)
#     email = Column("email", String(50))
#     password_salt = Column("password_salt", String(20))
#     password_hash = Column("password_hash", String)

#     def __init__(self, email: str, password_salt: str, password_hash: str):
#         self.email = email
#         self.password_salt = password_salt
#         self.password_hash = password_hash
    
#     def __repr__(self):
#         return f"User {self.pid}"