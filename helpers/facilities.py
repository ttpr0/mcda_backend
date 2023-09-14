# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Polygon
from sqlalchemy.orm import Session
from sqlalchemy import select

from models import ENGINE, Facility as FacilityTable


def get_facility(name: str, envelop: Polygon) -> tuple[list[tuple[float, float]], list[float]]:
    locations = []
    weights = []
    with Session(ENGINE) as session:
        stmt = select(FacilityTable.wgs_x, FacilityTable.wgs_y, FacilityTable.weight).where((FacilityTable.group==name) & FacilityTable.point.ST_Within(envelop.wkt))
        rows = session.execute(stmt).fetchall()
        for row in rows:
            wgs_x: float = row[0]
            wgs_y: float = row[1]
            weight: float = row[2]
            locations.append((wgs_x, wgs_y))
            weights.append(weight)
    return locations, weights
