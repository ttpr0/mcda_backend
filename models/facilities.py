# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import select
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session
from shapely import Point, Polygon

from . import ENGINE, get_table

def get_facility(facility_name: str, envelop: Polygon) -> tuple[list[tuple[float, float]], list[float]]:
    locations = []
    weights = []
    location_set = set()

    envelop_wkb = from_shape(envelop, srid=4326)

    with Session(ENGINE) as session:
        # get facility table and columns for the given facility
        list_table = get_table("facilities_list")
        if list_table is None:
            return (locations, weights)
        stmt = select(list_table.c.table_name, list_table.c.geometry_column, list_table.c.weight_column).where(list_table.c.name == facility_name)
        rows = session.execute(stmt).fetchall()
        table_name = None
        geometry_column = None
        weight_column = None
        for row in rows:
            table_name = row[0]
            geometry_column = row[1]
            weight_column = row[2]
        if table_name is None or geometry_column is None or weight_column is None:
            return (locations, weights)

        # read locations and weights from table
        facility_table = get_table(table_name)
        if facility_table is None:
            return (locations, weights)
        stmt = select(getattr(facility_table.c, geometry_column), getattr(facility_table.c, weight_column)).where(getattr(facility_table.c, geometry_column).ST_Within(envelop_wkb))
        rows = session.execute(stmt).fetchall()
        for row in rows:
            if row[1] == 0:
                continue
            point = to_shape(row[0])
            if (point.x, point.y) in location_set:
                continue
            location_set.add((point.x, point.y))
            locations.append((point.x, point.y))
            weights.append(row[1])
    return locations, weights

def _get_facility_group_by_id(session: Session, group_id: int) -> tuple[str, str, int] | None:
    """Retrives the facility-group by id.
    - None if no supply-level is found.
    - Return group-name, group-i18n-key and super-group-id (-1 if None)
    """
    group_table = get_table("facilities_groups")
    if group_table is None:
        return None
    stmt = select(group_table.c.name, group_table.c.i18n_key, group_table.c.super_group_id).where(group_table.c.group_id == group_id)
    rows = session.execute(stmt).fetchall()
    for row in rows:
        return str(row[0]), str(row[1]), row[2]
    return None

FACILITIES = {
    "localSupply": {
        "text": "localSupply.text",
        "items": {
            "supermarket": {"text": "localSupply.supermarket"},
            "discounter": {"text": "localSupply.discounter"},
            "other_local_supply": {"text": "localSupply.otherLocalSupply", "tooltip": "tooltip.otherLocalSupply"}
        }
    },
    "health": {
        "text": "health.text",
        "items": {
            "pharmacy": {"text": "health.pharmacy"},
            "clinic": {"text": "health.clinic"},
            "physicians": {"text": "health.physicians.text", "items": {
                "general_physician": {"text": "health.physicians.generalPhysicians"},
                "paediatrician": {"text": "health.physicians.paediatrician"},
                "ophthalmologist": {"text": "health.physicians.ophthalmologist"},
                "surgeon": {"text": "health.physicians.surgeon"},
                "gynaecologist": {"text": "health.physicians.gynaecologist"},
                "dermatologist": {"text": "health.physicians.dermatologist"},
                "otolaryngologist": {"text": "health.physicians.otolaryngologist"},
                "neurologist": {"text": "health.physicians.neurologist"},
                "psychotherapist": {"text": "health.physicians.psychotherapists"},
                "urologist": {"text": "health.physicians.urologists"}
            }
            }
        }
    },
    "education": {
        "text": "education.text",
        "items": {
            "nursery": {"text": "education.nursery", "tooltip": "tooltip.nursery"},
            "primary_school": {"text": "education.primarySchool", "tooltip": "tooltip.primarySchool"},
            "secondary_school_1": {"text": "education.secondarySchool1", "tooltip": "tooltip.secondarySchool1"},
            "secondary_school_2": {"text": "education.secondarySchool2", "tooltip": "tooltip.secondarySchool2"}
        }
    }
}

def get_available_facilities():
    # return FACILITIES
    facilities = {}
    facilities_table = get_table("facilities_list")
    if facilities_table is None:
        return facilities
    with Session(ENGINE) as session:
        stmt = select(facilities_table.c.name, facilities_table.c.i18n_key, facilities_table.c.tooltip_key, facilities_table.c.group_id).where()
        rows = session.execute(stmt).fetchall()
        for row in rows:
            name = str(row[0])
            i18n_key = str(row[1])
            tooltip_key = row[2]
            if tooltip_key is None:
                item = {"text": i18n_key}
            else:
                item = {"text": i18n_key, "tooltip": tooltip_key}
            group_id = int(row[3])
            group = _get_facility_group_by_id(session, group_id)
            if group is None:
                continue
            group_name, group_i18n_key, super_group_id = group
            if super_group_id is None:
                if group_name not in facilities:
                    facilities[group_name] = {"text": group_i18n_key, "items": {}}
                facilities[group_name]["items"][name] = item
            else:
                super_group = _get_facility_group_by_id(session, super_group_id)
                if super_group is None:
                    continue
                super_group_name, super_group_i18n_key, super_group_id = super_group
                if super_group_id is not None:
                    raise ValueError("only one-level of groups are allowed to have super-groups")
                if super_group_name not in facilities:
                    facilities[super_group_name] = {"text": super_group_i18n_key, "items": {}}
                group_facilities = facilities[super_group_name]["items"]
                if group_name not in group_facilities:
                    group_facilities[group_name] = {"text": group_i18n_key, "items": {}}
                group_facilities[group_name]["items"][name] = item
    return facilities
