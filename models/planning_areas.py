# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import create_engine, Column, Integer, String
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session, declarative_base
from shapely import Point, Polygon

# from . import Base

# class PlanningArea(Base):
#     __tablename__ = "planning_areas"

#     pid = Column("pid", Integer, primary_key=True, autoincrement=True)
#     name = Column("name", String(50))
#     geom = Column("geom", Geometry('POLYGON'))

#     def __init__(self, name: str, geom: Polygon):
#         self.name = name
#         self.geom = from_shape(geom)
    
#     def __repr__(self):
#         return f"id: {self.pid}, name: {self.name}"