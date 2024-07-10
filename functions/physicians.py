# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""Utility functions to retrive physicians from db.
"""

from sqlalchemy import select
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.ext.asyncio import AsyncSession
from shapely import Point, Polygon

from .util import get_table
from .planning_areas import _get_supply_level_by_id


async def get_physicians(session: AsyncSession, query: Polygon, physician_name: str, capacity_type: str) -> tuple[list[tuple[float, float]], list[float]]:
    """Retrives physicians from db.

    Args:
        session: db session
        query: extent to query physicians
        physician_name: physician name
        capacity_type: capacity type (e.g. location-based, scope of participation)

    Returns:
        lists of locations and weights

    Note:
        - a table physicians_list must exist in the database (containing metadata about existing physicians)
        - a table physicians_locations must exist in the database (containing the actual locations of physicians)
    """
    locations = []
    weights = []

    query_wkb = from_shape(query, srid=4326)
    
    phys_list = get_table("physicians_list")
    if phys_list is None:
        return (locations, weights)
    stmt = select(phys_list.c.physician_id).where(phys_list.c.name == physician_name)
    rows = await session.execute(stmt)
    rows = rows.fetchall()
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
        rows = await session.execute(stmt)
        rows = rows.fetchall()
        for row in rows:
            point = to_shape(row[0])
            locations.append((point.x, point.y))
            weights.append(1)
    elif capacity_type == 'physicianNumber':
        stmt = select(phys_locs.c.geometry, phys_locs.c.physician_count).where(
            (phys_locs.c.physician_id == detail_id) & phys_locs.c.geometry.ST_Within(query_wkb)
        )
        rows = await session.execute(stmt)
        rows = rows.fetchall()
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
        rows = await session.execute(stmt)
        rows = rows.fetchall()
        for row in rows:
            if row[1] == 0:
                continue
            point = to_shape(row[0])
            locations.append((point.x, point.y))
            weights.append(row[1])
    return (locations, weights)

async def get_available_physicians(session: AsyncSession) -> dict:
    """Retrives available physicians from db.

    Args:
        session: db session

    Returns:
        list of available physicians

    Note:
        - the format of returned data is expected by dva-fe (can be put into state directly)
        - future changes in the frontend might involve updating this function
        - a table physicians_list must exist in the database (containing metadata about existing physicians)
    """
    physician_groups = {}
    physician_table = get_table("physicians_list")
    if physician_table is None:
        return physician_groups
    stmt = select(physician_table.c.name, physician_table.c.i18n_key, physician_table.c.supply_level_ids).where()
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    for row in rows:
        name = str(row[0])
        i18n_key = str(row[1])
        level_ids = list(row[2])
        for level_id in level_ids:
            supply_level = await _get_supply_level_by_id(session, level_id)
            if supply_level not in physician_groups:
                physician_groups[supply_level] = {}
            physician_groups[supply_level][name] = {"text": i18n_key}
    return physician_groups
