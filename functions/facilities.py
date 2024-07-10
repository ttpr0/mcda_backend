# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""Utility functions to retrive facilities from db.
"""

from sqlalchemy import select
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.ext.asyncio import AsyncSession
from shapely import Point, Polygon

from .util import get_table

async def get_facility(session: AsyncSession, facility_name: str, envelop: Polygon) -> tuple[list[tuple[float, float]], list[float]]:
    """Extract facility locations and weights from the database.

    Args:
        session: sqlalchemy session
        facility_name: name of the facility
        envelop: envelop to filter facilities

    Returns:
        list of locations and weights

    Note:
        - a table facilities_list must exist in the database (containing metadata about existing facilites)
    """
    locations = []
    weights = []
    location_set = set()

    envelop_wkb = from_shape(envelop, srid=4326)

    # get facility table and columns for the given facility
    list_table = get_table("facilities_list")
    if list_table is None:
        return (locations, weights)
    stmt = select(list_table.c.table_name, list_table.c.geometry_column, list_table.c.weight_column).where(list_table.c.name == facility_name)
    rows = await session.execute(stmt)
    rows = rows.fetchall()
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
    rows = await session.execute(stmt)
    rows = rows.fetchall()
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

async def _get_facility_group_by_id(session: AsyncSession, group_id: int) -> tuple[str, str, int] | None:
    """Retrives the facility-group by id.
    - None if no supply-level is found.
    - Return group-name, group-i18n-key and super-group-id (-1 if None)
    """
    group_table = get_table("facilities_groups")
    if group_table is None:
        return None
    stmt = select(group_table.c.name, group_table.c.i18n_key, group_table.c.super_group_id).where(group_table.c.group_id == group_id)
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    for row in rows:
        return str(row[0]), str(row[1]), row[2]
    return None

async def get_available_facilities(session: AsyncSession) -> dict:
    """Retrives all available facilities.

    Args:
        session: sqlalchemy session

    Returns:
        dict of available facilities (for format see dva-fe example state)

    Note:
        - this function returns data as expected by dva-fe (can be put into state directly)
        - future changes in the frontend might involve updating this function
        - a table facilities_list must exist in the database (containing metadata about existing facilites)
    """
    facilities = {}
    facilities_table = get_table("facilities_list")
    if facilities_table is None:
        return facilities
    stmt = select(facilities_table.c.name, facilities_table.c.i18n_key, facilities_table.c.tooltip_key, facilities_table.c.group_id).where()
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    for row in rows:
        name = str(row[0])
        i18n_key = str(row[1])
        tooltip_key = row[2]
        if tooltip_key is None:
            item = {"text": i18n_key}
        else:
            item = {"text": i18n_key, "tooltip": tooltip_key}
        group_id = int(row[3])
        group = await _get_facility_group_by_id(session, group_id)
        if group is None:
            continue
        group_name, group_i18n_key, super_group_id = group
        if super_group_id is None:
            if group_name not in facilities:
                facilities[group_name] = {"text": group_i18n_key, "items": {}}
            facilities[group_name]["items"][name] = item
        else:
            super_group = await _get_facility_group_by_id(session, super_group_id)
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
