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

SUPPLY_LEVELS = {
    "generalPhysician": {"text": "Hausärztliche Versorgung - Versorgungsebene 1", "valid": True},
    "generalSpecialist": {"text": "Allgemeine fachärztliche Versorgung  - Versorgungsebene 2", "valid": True},
    "specializedSpecialist": {"text": "Spezialisierte fachärztliche Versorgung - Versorgungsebene 3", "valid": False},
    "lowerSaxony": {"text": "Niedersachsen - Versorgungsebene / KV-Bezirk", "valid": True}
}

PLANNING_AREAS = {
    "generalPhysician": {
        "aurich": {"text": "Aurich"},
        "emden": {"text": "Emden"},
        "jever": {"text": "Jever"},
        "norden": {"text": "Norden"},
        "varel": {"text": "Varel"},
        "wilhelmshaven": {"text": "Wilhelmshaven"},
        "wittmund": {"text": "Wittmund"}
    },
    "generalSpecialist": {
        "aurich": {"text": "Aurich"},
        "emden": {"text": "Emden"},
        "jever": {"text": "Jever"},
        "norden": {"text": "Norden"},
        "varel": {"text": "Varel"},
        "wilhelmshaven": {"text": "Wilhelmshaven"},
        "wittmund": {"text": "Wittmund"}
    },
    "specializedSpecialist": {
    },
    "lowerSaxony": {
        "niedersachsen": {"text": "Niedersachsen"},
        "kv_bezirk": {"text": "KV-Bezirk"},
    }
}

def get_available_supply_levels():
    return SUPPLY_LEVELS

def get_available_planning_areas():
    return PLANNING_AREAS
