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
    "generalPhysician": {"text": "supplyLevels.generalPhysician", "valid": True},
    "generalSpecialist": {"text": "supplyLevels.generalSpecialist", "valid": True},
    "specializedSpecialist": {"text": "supplyLevels.specializedSpecialist", "valid": False},
    "lowerSaxony": {"text": "supplyLevels.lowerSaxony", "valid": True}
}

PLANNING_AREAS = {
    "generalPhysician": {
        "aurich": {"text": "planningAreas.aurich"},
        "emden": {"text": "planningAreas.emden"},
        "jever": {"text": "planningAreas.jever"},
        "norden": {"text": "planningAreas.norden"},
        "varel": {"text": "planningAreas.varel"},
        "wilhelmshaven": {"text": "planningAreas.wilhelmshaven"},
        "wittmund": {"text": "planningAreas.wittmund"}
    },
    "generalSpecialist": {
        "aurich": {"text": "planningAreas.aurich"},
        "emden": {"text": "planningAreas.emden"},
        "jever": {"text": "planningAreas.jever"},
        "norden": {"text": "planningAreas.norden"},
        "varel": {"text": "planningAreas.varel"},
        "wilhelmshaven": {"text": "planningAreas.wilhelmshaven"},
        "wittmund": {"text": "planningAreas.wittmund"}
    },
    "specializedSpecialist": {
    },
    "lowerSaxony": {
        "niedersachsen": {"text": "planningAreas.niedersachsen"},
        "kv_bezirk": {"text": "planningAreas.kv_bezirk"},
    }
}

def get_available_supply_levels():
    return SUPPLY_LEVELS

def get_available_planning_areas():
    return PLANNING_AREAS
