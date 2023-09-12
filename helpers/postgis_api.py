# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import Column, Integer, Float, select, insert, update, delete
from geoalchemy2 import Geometry
from shapely import Point, Polygon

from models import ENGINE, create_table

ACCESSIBILITY_SPEC = [
    Column("pid", Integer, primary_key=True, autoincrement=True),
    Column("access", Float),
    Column("geom", Geometry('POLYGON')),
]
    
access_table = create_table("access", ACCESSIBILITY_SPEC)

def build_wkt(x: float, y: float) -> str:
    return f"Polygon(({x-50} {y-50}, {x+50} {y-50}, {x+50} {y+50}, {x-50} {y+50}, {x-50} {y-50}))"

def add_results(values: list[tuple[float, float, float]]):
    with ENGINE.connect() as conn:
        stmt = delete(access_table).where()
        conn.execute(stmt)

        data = [{"access": a, "geom": build_wkt(x, y)} for i, (a, x, y) in enumerate(values)]
        stmt = insert(access_table).values(data)
        conn.execute(stmt)
        conn.commit()
        
