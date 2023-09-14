# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon, contains_xy
from sqlalchemy import select
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

import config

from models import ENGINE, PlanningArea, PhysiciansLocationBased, PhysiciansCountBased, PhysiciansList

def get_planning_area(supply_level: str, planning_area: str) -> Polygon|None:
    with Session(ENGINE) as session:
        stmt = select(PlanningArea.geom).where(PlanningArea.name == planning_area)
        rows = session.execute(stmt).fetchall()
        for row in rows:
            return to_shape(row[0])
        return None

def get_physicians(query: Polygon, supply_level: str, facility_type: str, facility_cap: str) -> tuple[list[tuple[float, float]], list[float]]:    
    locations = []
    weights = []
    
    with Session(ENGINE) as session:
        stmt = select(PhysiciansList.detail_id).where(PhysiciansList.name == facility_type)
        rows = session.execute(stmt).fetchall()
        detail_id = None
        for row in rows:
            detail_id = row[0]
        if detail_id is None:
            return (locations, weights)

        if facility_cap == 'facility':
            stmt = select(PhysiciansLocationBased.point, PhysiciansLocationBased.count).where(
                (PhysiciansLocationBased.detail_id == detail_id) & PhysiciansLocationBased.point.ST_Within(query.wkt)
            )
            rows = session.execute(stmt).fetchall()
            for row in rows:
                point = to_shape(row[0])
                locations.append((point.x, point.y))
                weights.append(row[1])
        elif facility_cap == 'physicianNumber':
            stmt = select(PhysiciansCountBased.point, PhysiciansCountBased.vbe_sum).where(
                (PhysiciansCountBased.detail_id == detail_id) & PhysiciansCountBased.point.ST_Within(query.wkt)
            )
            rows = session.execute(stmt).fetchall()
            for row in rows:
                point = to_shape(row[0])
                locations.append((point.x, point.y))
                weights.append(row[1])
        elif facility_cap == 'employmentVolume':
            stmt = select(PhysiciansCountBased.point, PhysiciansCountBased.pys_count).where(
                (PhysiciansCountBased.detail_id == detail_id) & PhysiciansCountBased.point.ST_Within(query.wkt)
            )
            rows = session.execute(stmt).fetchall()
            for row in rows:
                point = to_shape(row[0])
                locations.append((point.x, point.y))
                weights.append(row[1])
    
    return (locations, weights)