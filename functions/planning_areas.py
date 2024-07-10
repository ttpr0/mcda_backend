# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""Utility functions to retrive planning areas from db.
"""

from sqlalchemy import select
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.ext.asyncio import AsyncSession
from shapely import Point, Polygon

from .util import get_table


async def get_planning_area(session: AsyncSession, planning_area: str) -> Polygon | None:
    """Retrives a planning-area by name.

    Args:
        session: db session
        planning_area: name of the planning-area

    Returns:
        Polygon of the planning-area
    """
    area_table = get_table("planning_areas")
    if area_table is None:
        return None
    stmt = select(area_table.c.geometry).where(area_table.c.name == planning_area)
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    for row in rows:
        return to_shape(row[0])
    return None

async def _get_supply_level_by_id(session: AsyncSession, supply_level_id: int) -> str | None:
    """Retrives the supply-level NAME by id.
    - None if no supply-level is found.
    """
    level_table = get_table("supply_level_list")
    if level_table is None:
        return None
    stmt = select(level_table.c.name).where(level_table.c.supply_level_id == supply_level_id)
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    for row in rows:
        return str(row[0])
    return None

async def get_available_supply_levels(session: AsyncSession) -> dict:
    """Retrives the available supply-levels.

    Args:
        session: db session

    Returns:
        dict of available supply-levels (as expected by dva-fe)
    """
    supply_levels = {}
    level_table = get_table("supply_level_list")
    if level_table is None:
        return supply_levels
    stmt = select(level_table.c.name, level_table.c.i18n_key, level_table.c.valid).where()
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    for row in rows:
        name = str(row[0])
        i18n_key = str(row[1])
        valid = bool(row[2])
        supply_levels[name] = {"text": i18n_key, "valid": valid}
    return supply_levels

async def get_available_planning_areas(session: AsyncSession) -> dict:
    """Retrives the available planning-areas.

    Args:
        session: db session

    Returns:
        dict of available planning-areas (as expected by dva-fe)
    """
    planning_areas = {}
    area_table = get_table("planning_areas")
    if area_table is None:
        return planning_areas
    stmt = select(area_table.c.name, area_table.c.i18n_key, area_table.c.supply_level_ids).where()
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    for row in rows:
        name = str(row[0])
        i18n_key = str(row[1])
        level_ids = list(row[2])
        for level_id in level_ids:
            supply_level = await _get_supply_level_by_id(session, level_id)
            if supply_level not in planning_areas:
                planning_areas[supply_level] = {}
            planning_areas[supply_level][name] = {"text": i18n_key}
    return planning_areas
