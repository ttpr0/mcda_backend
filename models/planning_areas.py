# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import select
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session, declarative_base
from shapely import Point, Polygon

from . import ENGINE, get_table


def get_planning_area(planning_area: str) -> Polygon | None:
    area_table = get_table("planning_areas")
    if area_table is None:
        return None
    with Session(ENGINE) as session:
        stmt = select(area_table.c.GEOMETRY).where(area_table.c.NAME == planning_area)
        rows = session.execute(stmt).fetchall()
        for row in rows:
            return to_shape(row[0])
        return None

def _get_supply_level_by_id(session: Session, supply_level_id: int) -> str | None:
    """Retrives the supply-level NAME by id.
    - None if no supply-level is found.
    """
    level_table = get_table("supply_level_list")
    if level_table is None:
        return None
    stmt = select(level_table.c.NAME).where(level_table.c.SUPPLY_LEVEL_ID == supply_level_id)
    rows = session.execute(stmt).fetchall()
    for row in rows:
        return str(row[0])
    return None

SUPPLY_LEVELS = {
    "generalPhysician": {"text": "supplyLevels.generalPhysician", "valid": True},
    "generalSpecialist": {"text": "supplyLevels.generalSpecialist", "valid": True},
    "specializedSpecialist": {"text": "supplyLevels.specializedSpecialist", "valid": False},
    "lowerSaxony": {"text": "supplyLevels.lowerSaxony", "valid": True}
}

def get_available_supply_levels():
    # return SUPPLY_LEVELS
    supply_levels = {}
    level_table = get_table("supply_level_list")
    if level_table is None:
        return supply_levels
    with Session(ENGINE) as session:
        stmt = select(level_table.c.NAME, level_table.c.I18N_KEY, level_table.c.VALID).where()
        rows = session.execute(stmt).fetchall()
        for row in rows:
            name = str(row[0])
            i18n_key = str(row[1])
            valid = bool(row[2])
            supply_levels[name] = {"text": i18n_key, "valid": valid}
    return supply_levels

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

def get_available_planning_areas():
    # return PLANNING_AREAS
    planning_areas = {}
    area_table = get_table("planning_areas")
    if area_table is None:
        return planning_areas
    with Session(ENGINE) as session:
        stmt = select(area_table.c.NAME, area_table.c.I18N_KEY, area_table.c.SUPPLY_LEVEL_IDS).where()
        rows = session.execute(stmt).fetchall()
        for row in rows:
            name = str(row[0])
            i18n_key = str(row[1])
            level_ids = list(row[2])
            for level_id in level_ids:
                supply_level = _get_supply_level_by_id(session, level_id)
                if supply_level not in planning_areas:
                    planning_areas[supply_level] = {}
                planning_areas[supply_level][name] = {"text": i18n_key}
    return planning_areas
