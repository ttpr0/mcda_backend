# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import select
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session, declarative_base
from shapely import Point, Polygon

from . import ENGINE, get_table

def get_planning_area(supply_level: str, planning_area: str) -> Polygon|None:
    area_table = get_table("planning_areas")
    if area_table is None:
        return None
    with Session(ENGINE) as session:
        stmt = select(area_table.c.geom).where(area_table.c.name == planning_area)
        rows = session.execute(stmt).fetchall()
        for row in rows:
            return to_shape(row[0])
        return None

def get_physicians(query: Polygon, supply_level: str, facility_type: str, facility_cap: str) -> tuple[list[tuple[float, float]], list[float]]:
    locations = []
    weights = []
    
    with Session(ENGINE) as session:
        phys_list = get_table("physicians_list")
        if phys_list is None:
            return (locations, weights)
        stmt = select(phys_list.c.DETAIL_ID).where(phys_list.c.name == facility_type)
        rows = session.execute(stmt).fetchall()
        detail_id = None
        for row in rows:
            detail_id = row[0]
        if detail_id is None:
            return (locations, weights)

        if facility_cap == 'facility':
            phys_loc_based = get_table("physicians_location_based")
            if phys_loc_based is None:
                return (locations, weights)
            stmt = select(phys_loc_based.c.point, phys_loc_based.c.count).where(
                (phys_loc_based.c.DETAIL_ID == detail_id) & phys_loc_based.c.point.ST_Within(query.wkt)
            )
            rows = session.execute(stmt).fetchall()
            for row in rows:
                point = to_shape(row[0])
                locations.append((point.x, point.y))
                weights.append(row[1])
        elif facility_cap == 'physicianNumber':
            phys_count_based = get_table("physicians_count_based")
            if phys_count_based is None:
                return (locations, weights)
            stmt = select(phys_count_based.c.point, phys_count_based.c.VBE_Sum).where(
                (phys_count_based.c.DETAIL_ID == detail_id) & phys_count_based.c.point.ST_Within(query.wkt)
            )
            rows = session.execute(stmt).fetchall()
            for row in rows:
                point = to_shape(row[0])
                locations.append((point.x, point.y))
                weights.append(row[1])
        elif facility_cap == 'employmentVolume':
            phys_count_based = get_table("physicians_count_based")
            if phys_count_based is None:
                return (locations, weights)
            stmt = select(phys_count_based.c.point, phys_count_based.c.Pys_Count).where(
                (phys_count_based.c.DETAIL_ID == detail_id) & phys_count_based.c.point.ST_Within(query.wkt)
            )
            rows = session.execute(stmt).fetchall()
            for row in rows:
                point = to_shape(row[0])
                locations.append((point.x, point.y))
                weights.append(row[1])
    
    return (locations, weights)

# from . import Base


# class SupplyLevelList(Base):
#     __tablename__ = "supply_level_list"

#     pid = Column("pid", Integer, primary_key=True, autoincrement=True)
#     name = Column("name", String(50))
#     typ_id = Column("TYP_ID", Integer)

#     def __init__(self, name: str, typ_id: int):
#         self.name = name
#         self.typ_id = typ_id
    
#     def __repr__(self):
#         return f"id: {self.pid}, typ: {self.typ_id}"

# class PhysiciansList(Base):
#     __tablename__ = "physicians_list"

#     pid = Column("pid", Integer, primary_key=True, autoincrement=True)
#     name = Column("name", String(50))
#     typ_id = Column("TYP_ID", Integer)
#     detail_id = Column("DETAIL_ID", Integer)

#     def __init__(self, name: str, typ_id: int, detail_id: int):
#         self.name = name
#         self.typ_id = typ_id
#         self.detail_id = detail_id
    
#     def __repr__(self):
#         return f"id: {self.pid}, typ: {self.typ_id}"

# class PhysiciansLocationBased(Base):
#     __tablename__ = "physicians_location_based"

#     pid = Column("pid", Integer, primary_key=True, autoincrement=True)
#     point = Column("point", Geometry('POINT'))
#     typ_id = Column("TYP_ID", Integer)
#     detail_id = Column("DETAIL_ID", Integer)
#     count = Column("count", Integer)

#     def __init__(self, point: Point, typ_id: int, detail_id: int):
#         self.point = from_shape(point)
#         self.typ_id = typ_id
#         self.detail_id = detail_id
#         self.count = 1
    
#     def __repr__(self):
#         return f"id: {self.pid}, typ: {self.typ_id}"
    
# class PhysiciansCountBased(Base):
#     __tablename__ = "physicians_count_based"

#     pid = Column("pid", Integer, primary_key=True, autoincrement=True)
#     point = Column("point", Geometry('POINT'))
#     typ_id = Column("TYP_ID", Integer)
#     detail_id = Column("DETAIL_ID", Integer)
#     vbe_sum = Column("VBE_Sum", Float)
#     pys_count = Column("Pys_Count", Float)

#     def __init__(self, point: Point, typ_id: int, detail_id: int, vbe_sum: float, pys_count: float):
#         self.point = from_shape(point)
#         self.typ_id = typ_id
#         self.detail_id = detail_id
#         self.vbe_sum = vbe_sum
#         self.pys_count = pys_count
    
#     def __repr__(self):
#         return f"id: {self.pid}, typ: {self.typ_id}"