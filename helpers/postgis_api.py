# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import create_engine, Column, Integer, Float
from geoalchemy2 import Geometry
from sqlalchemy.orm import Session, declarative_base
from shapely import Point, Polygon

import config

engine = create_engine(f"postgresql+psycopg2://user:password@{config.POSTGIS_HOST}:5432/dvan")

Base = declarative_base()

class Accessibility(Base):
    __tablename__ = "access"

    pid = Column("pid", Integer, primary_key=True, autoincrement=True)
    access = Column("access", Float)
    point = Column("geom", Geometry('POINT'))

    def __init__(self, access: float, point: Point):
        self.access = access
        self.point = point.wkt
    
    def __repr__(self):
        return f"id: {self.pid}, name: {self.name}"
    
Base.metadata.create_all(engine)

def add_results(values: tuple[float, Point]):
    with Session(engine) as session:
        session.query(Accessibility).delete()

        for a, p in values:
            session.add(Accessibility(a, p))

        session.commit()
        
