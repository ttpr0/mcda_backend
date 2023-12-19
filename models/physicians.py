# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import select
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session, declarative_base
from shapely import Point, Polygon

from . import ENGINE, get_table


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

PHYSICIAN_GROUPS = {
    "generalPhysician": {
        "general_physician": {"text": "Hausärzte"}
    },
    "generalSpecialist": {
        "augenarzte": {"text": "Augenärzte"},
        "surgeon": {"text": "Chirurgen und Orthopäden"},
        "frauenarzte": {"text": "Frauenärzte"},
        "dermatologist": {"text": "Hautärzte"},
        "hno_arzte": {"text": "HNO-Ärzte"},
        "paediatrician": {"text": "Kinderärzte"},
        "neurologist": {"text": "Nervenärzte"},
        "psychotherapist": {"text": "Psychotherapeuten"},
        "urologist": {"text": "Urologen"}
    },
    "specializedSpecialist": {
        "internisten": {"text": "fachärztlich tätige Internisten"},
        "jugendpsychiater": {"text": "Kinder- und Jugendpsychiater"},
        "radiologen": {"text": "Radiologen"},
        "anasthesisten": {"text": "Anästhesisten"}
    },
    "lowerSaxony": {
        "augenarzte": {"text": "Augenärzte"},
        "surgeon": {"text": "Chirurgen und Orthopäden"},
        "frauenarzte": {"text": "Frauenärzte"},
        "dermatologist": {"text": "Hautärzte"},
        "hno_arzte": {"text": "HNO-Ärzte"},
        "paediatrician": {"text": "Kinderärzte"},
        "neurologist": {"text": "Nervenärzte"},
        "psychotherapist": {"text": "Psychotherapeuten"},
        "urologist": {"text": "Urologen"},
        "internisten": {"text": "fachärztlich tätige Internisten"},
        "jugendpsychiater": {"text": "Kinder- und Jugendpsychiater"},
        "radiologen": {"text": "Radiologen"},
        "anasthesisten": {"text": "Anästhesisten"}
    }
}

def get_available_physicians():
    return PHYSICIAN_GROUPS
