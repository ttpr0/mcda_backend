# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import create_engine, Column, Integer, String, Float
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session, declarative_base
from shapely import Point, Polygon

from . import Base


class SupplyLevelList(Base):
    __tablename__ = "supply_level_list"

    pid = Column("pid", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(50))
    typ_id = Column("TYP_ID", Integer)

    def __init__(self, name: str, typ_id: int):
        self.name = name
        self.typ_id = typ_id
    
    def __repr__(self):
        return f"id: {self.pid}, typ: {self.typ_id}"

class PhysiciansList(Base):
    __tablename__ = "physicians_list"

    pid = Column("pid", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(50))
    typ_id = Column("TYP_ID", Integer)
    detail_id = Column("DETAIL_ID", Integer)

    def __init__(self, name: str, typ_id: int, detail_id: int):
        self.name = name
        self.typ_id = typ_id
        self.detail_id = detail_id
    
    def __repr__(self):
        return f"id: {self.pid}, typ: {self.typ_id}"

class PhysiciansLocationBased(Base):
    __tablename__ = "physicians_location_based"

    pid = Column("pid", Integer, primary_key=True, autoincrement=True)
    point = Column("point", Geometry('POINT'))
    typ_id = Column("TYP_ID", Integer)
    detail_id = Column("DETAIL_ID", Integer)
    count = Column("count", Integer)

    def __init__(self, point: Point, typ_id: int, detail_id: int):
        self.point = from_shape(point)
        self.typ_id = typ_id
        self.detail_id = detail_id
        self.count = 1
    
    def __repr__(self):
        return f"id: {self.pid}, typ: {self.typ_id}"
    
class PhysiciansCountBased(Base):
    __tablename__ = "physicians_count_based"

    pid = Column("pid", Integer, primary_key=True, autoincrement=True)
    point = Column("point", Geometry('POINT'))
    typ_id = Column("TYP_ID", Integer)
    detail_id = Column("DETAIL_ID", Integer)
    vbe_sum = Column("VBE_Sum", Float)
    pys_count = Column("Pys_Count", Float)

    def __init__(self, point: Point, typ_id: int, detail_id: int, vbe_sum: float, pys_count: float):
        self.point = from_shape(point)
        self.typ_id = typ_id
        self.detail_id = detail_id
        self.vbe_sum = vbe_sum
        self.pys_count = pys_count
    
    def __repr__(self):
        return f"id: {self.pid}, typ: {self.typ_id}"