# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import create_engine, Column, Integer, String, Float
from geoalchemy2 import Geometry
from sqlalchemy.orm import Session, declarative_base
from shapely import Point, Polygon

from . import Base

class Population(Base):
    __tablename__ = "population"

    pid = Column("pid", Integer, primary_key=True, autoincrement=True)
    point = Column("point", Geometry('POINT'), index=True)
    wgs_x = Column("wgs_x", Float)
    wgs_y = Column("wgs_y", Float)
    utm_x = Column("utm_x", Float)
    utm_y = Column("utm_y", Float)

    ew_gesamt = Column("ew_gesamt", Integer)
    stnd00_09 = Column("std_00_09", Integer)
    stnd10_19 = Column("std_10_19", Integer)
    stnd20_39 = Column("std_20_39", Integer)
    stnd40_59 = Column("std_40_59", Integer)
    stnd60_79 = Column("std_60_79", Integer)
    stnd80x = Column("std_80x", Integer)
    kisc00_02 = Column("ksc_00_02", Integer)
    kisc03_05 = Column("ksc_03_05", Integer)
    kisc06_09 = Column("ksc_06_09", Integer)
    kisc10_14 = Column("ksc_10_14", Integer)
    kisc15_17 = Column("ksc_15_17", Integer)
    kisc18_19 = Column("ksc_18_19", Integer)
    kisc20x = Column("ksc_20x", Integer)


    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"User {self.pid}"