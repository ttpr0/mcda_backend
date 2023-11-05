# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import select
from geoalchemy2.shape import from_shape
from sqlalchemy.orm import Session
from shapely import Point, Polygon

from . import ENGINE, get_table

def get_facility(name: str, envelop: Polygon) -> tuple[list[tuple[float, float]], list[float]]:
    locations = []
    weights = []
    with Session(ENGINE) as session:
        facility_table = get_table("facilities")
        if facility_table is None:
            return (locations, weights)
        stmt = select(facility_table.c.wgs_x, facility_table.c.wgs_y, facility_table.c.weight).where((facility_table.c.group==name) & facility_table.c.point.ST_Within(envelop.wkt))
        rows = session.execute(stmt).fetchall()
        for row in rows:
            wgs_x: float = row[0]
            wgs_y: float = row[1]
            weight: float = row[2]
            locations.append((wgs_x, wgs_y))
            weights.append(weight)
    return locations, weights

# from . import Base

# class Facility(Base):
#     __tablename__ = "facilities"

#     pid = Column("pid", Integer, primary_key=True, autoincrement=True)
#     group = Column("group", String)
#     point = Column("point", Geometry('POINT'), index=True)
#     wgs_x = Column("wgs_x", Float)
#     wgs_y = Column("wgs_y", Float)
#     weight = Column("weight", Float)


#     def __init__(self, group: str, point: Point, weight: float):
#         self.group = group
#         self.point = from_shape(point)
#         self.wgs_x = point.x
#         self.wgs_y = point.y
#         self.weight = weight
    
#     def __repr__(self):
#         return f"User {self.pid}"