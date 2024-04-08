# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import select
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session, declarative_base
from shapely import Point, Polygon

from . import ENGINE, get_table
from .planning_areas import _get_supply_level_by_id


def get_physicians(query: Polygon, physician_name: str, capacity_type: str) -> tuple[list[tuple[float, float]], list[float]]:
    locations = []
    weights = []

    query_wkb = from_shape(query, srid=4326)
    
    with Session(ENGINE) as session:
        phys_list = get_table("physicians_list")
        if phys_list is None:
            return (locations, weights)
        stmt = select(phys_list.c.physician_id).where(phys_list.c.name == physician_name)
        rows = session.execute(stmt).fetchall()
        detail_id = None
        for row in rows:
            detail_id = row[0]
        if detail_id is None:
            return (locations, weights)

        phys_locs = get_table("physicians_locations")
        if phys_locs is None:
            return (locations, weights)
        if capacity_type == 'facility':
            stmt = select(phys_locs.c.geometry).where(
                (phys_locs.c.physician_id == detail_id) & phys_locs.c.geometry.ST_Within(query_wkb)
            )
            rows = session.execute(stmt).fetchall()
            for row in rows:
                point = to_shape(row[0])
                locations.append((point.x, point.y))
                weights.append(1)
        elif capacity_type == 'physicianNumber':
            stmt = select(phys_locs.c.geometry, phys_locs.c.physician_count).where(
                (phys_locs.c.physician_id == detail_id) & phys_locs.c.geometry.ST_Within(query_wkb)
            )
            rows = session.execute(stmt).fetchall()
            for row in rows:
                if row[1] == 0:
                    continue
                point = to_shape(row[0])
                locations.append((point.x, point.y))
                weights.append(row[1])
        elif capacity_type == 'employmentVolume':
            stmt = select(phys_locs.c.geometry, phys_locs.c.vbe_volume).where(
                (phys_locs.c.physician_id == detail_id) & phys_locs.c.geometry.ST_Within(query_wkb)
            )
            rows = session.execute(stmt).fetchall()
            for row in rows:
                if row[1] == 0:
                    continue
                point = to_shape(row[0])
                locations.append((point.x, point.y))
                weights.append(row[1])
    return (locations, weights)

PHYSICIAN_GROUPS = {
    "generalPhysician": {
        "general_physician": {"text": "physicians.generalPhysician"}
    },
    "generalSpecialist": {
        "augenarzte": {"text": "physicians.augenarzte"},
        "surgeon": {"text": "physicians.surgeon"},
        "frauenarzte": {"text": "physicians.frauenarzte"},
        "dermatologist": {"text": "physicians.dermatologist"},
        "hno_arzte": {"text": "physicians.hnoArzte"},
        "paediatrician": {"text": "physicians.paediatrician"},
        "neurologist": {"text": "physicians.neurologist"},
        "psychotherapist": {"text": "physicians.psychotherapist"},
        "urologist": {"text": "physicians.urologist"}
    },
    "specializedSpecialist": {
        "internisten": {"text": "physicians.internisten"},
        "jugendpsychiater": {"text": "physicians.jugendpsychiater"},
        "radiologen": {"text": "physicians.radiologen"},
        "anasthesisten": {"text": "physicians.anasthesisten"}
    },
    "lowerSaxony": {
        "augenarzte": {"text": "physicians.augenarzte"},
        "surgeon": {"text": "physicians.surgeon"},
        "frauenarzte": {"text": "physicians.frauenarzte"},
        "dermatologist": {"text": "physicians.dermatologist"},
        "hno_arzte": {"text": "physicians.hnoArzte"},
        "paediatrician": {"text": "physicians.paediatrician"},
        "neurologist": {"text": "physicians.neurologist"},
        "psychotherapist": {"text": "physicians.psychotherapist"},
        "urologist": {"text": "physicians.urologist"},
        "internisten": {"text": "physicians.internisten"},
        "jugendpsychiater": {"text": "physicians.jugendpsychiater"},
        "radiologen": {"text": "physicians.radiologen"},
        "anasthesisten": {"text": "physicians.anasthesisten"}
    }
}

def get_available_physicians():
    # return PHYSICIAN_GROUPS
    physician_groups = {}
    physician_table = get_table("physicians_list")
    if physician_table is None:
        return physician_groups
    with Session(ENGINE) as session:
        stmt = select(physician_table.c.name, physician_table.c.i18n_key, physician_table.c.supply_level_ids).where()
        rows = session.execute(stmt).fetchall()
        for row in rows:
            name = str(row[0])
            i18n_key = str(row[1])
            level_ids = list(row[2])
            for level_id in level_ids:
                supply_level = _get_supply_level_by_id(session, level_id)
                if supply_level not in physician_groups:
                    physician_groups[supply_level] = {}
                physician_groups[supply_level][name] = {"text": i18n_key}
    return physician_groups
