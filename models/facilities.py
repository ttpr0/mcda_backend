# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import create_engine, Column, Integer, String, Float
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape
from sqlalchemy.orm import Session, declarative_base
from shapely import Point, Polygon

from . import Base

class Facility(Base):
    __tablename__ = "facilities"

    pid = Column("pid", Integer, primary_key=True, autoincrement=True)
    group = Column("group", String)
    point = Column("point", Geometry('POINT'), index=True)
    wgs_x = Column("wgs_x", Float)
    wgs_y = Column("wgs_y", Float)
    weight = Column("weight", Float)


    def __init__(self, group: str, point: Point, weight: float):
        self.group = group
        self.point = from_shape(point)
        self.wgs_x = point.x
        self.wgs_y = point.y
        self.weight = weight
    
    def __repr__(self):
        return f"User {self.pid}"