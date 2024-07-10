# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""Utility functions to retrive population-grid from db.
"""

from sqlalchemy import select, func
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.ext.asyncio import AsyncSession
from shapely import Point, Polygon, from_wkb, STRtree

from .util import get_table
from helpers.util import deprecated

@deprecated
async def get_population(session: AsyncSession, query: Polygon, typ: str = 'standard_all', age_groups: list[str] = []) -> tuple[list[tuple[float, float]], list[tuple[float, float]], list[int]]:
    """Only kept for backwards compatibility. If it is not used anymore, please remove it.
    """
    locations: list[tuple[float, float]] = []
    utm_locations: list[tuple[float, float]] = []
    weights: list[int] = []

    query_wkb = from_shape(query, srid=4326)

    list_table = get_table("population_list")
    if list_table is None:
        return locations, utm_locations, weights
    # get population name
    name = typ
    if typ == "standard_all":
        name = "standard"
    # get population tables
    stmt = select(list_table.c.table_name, list_table.c.meta_table_name).where(list_table.c.name == name)
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    table_name = None
    meta_table_name = None
    for row in rows:
        table_name = row[0]
        meta_table_name = row[1]
    if table_name is None or meta_table_name is None:
        return locations, utm_locations, weights
    # get population keys
    keys = age_groups
    if typ == "standard_all":
        meta_table = get_table(meta_table_name)
        if meta_table is None:
            return locations, utm_locations, weights
        stmt = select(meta_table.c.age_group_key).where()
        rows = await session.execute(stmt)
        rows = rows.fetchall()
        keys = []
        for row in rows:
            keys.append(row[0])
    # get population sum
    pop_table = get_table(table_name)
    if pop_table is None:
        return locations, utm_locations, weights
    if len(keys) == 0:
        return locations, utm_locations, weights
    age_sum = getattr(pop_table.c, keys[0])
    for key in keys[1:]:
        age_sum = age_sum + getattr(pop_table.c, key)
    stmt = select(pop_table.c.x, pop_table.c.y, pop_table.c.utm_x, pop_table.c.utm_y, age_sum).where(pop_table.c.geometry.ST_Within(query_wkb))
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    for row in rows:
        if row[4] == 0:
            continue
        locations.append((row[0], row[1]))
        utm_locations.append((row[2], row[3]))
        weights.append(row[4])
    return locations, utm_locations, weights

async def get_population_values(session: AsyncSession, query: Polygon | None = None, indices: list[int] | None = None, typ: str = 'standard_all', age_groups: list[str] = []) -> tuple[list[tuple[float, float]], list[int]]:
    """Retrives the population data (location and weight) for a given population dataset.

    Result contains population cells within the query extent or part of indices-list. First n values of the result are garanteed to be ordered by indices-list (e.g. [indices[0], indices[1], ..., indices[-1], rest...]).
    
    Args:
        session: database session
        query: query extent (optional, only used if indices is None)
        indices: list of population grid-cell indices to get population data for 
        typ: population type (e.g. standard, kita_schul)
        age_groups: list of age groups (keys of population entries in db table)

    Returns:
        locations: list of population locations (centroid of cell)
        weights: list of population weights (sum of population in cell)

    Note:
        - this function should be called to retrive actual population data for accessibility calculations
        - most common workflow is to first retrive geometry using "get_population_geometry" for visualization purposes and then call this function to compute accessibility results
    """
    if query is None and indices is None:
        return [], []

    list_table = get_table("population_list")
    if list_table is None:
        return [], []
    if indices is not None:
        index_mapping = {}
        for i, id in enumerate(indices):
            index_mapping[id] = i
        locations: list[tuple[float, float]] = [(0, 0)] * len(indices)
        weights: list[int] = [0] * len(indices)
    else:
        locations: list[tuple[float, float]] = []
        weights: list[int] = []
    # get population name
    name = typ
    if typ == "standard_all":
        name = "standard"
    # get population tables
    stmt = select(list_table.c.table_name, list_table.c.meta_table_name).where(list_table.c.name == name)
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    table_name = None
    meta_table_name = None
    for row in rows:
        table_name = row[0]
        meta_table_name = row[1]
    if table_name is None or meta_table_name is None:
        return [], []
    # get population keys
    keys = age_groups
    if typ == "standard_all":
        meta_table = get_table(meta_table_name)
        if meta_table is None:
            return [], []
        stmt = select(meta_table.c.age_group_key).where()
        rows = await session.execute(stmt)
        rows = rows.fetchall()
        keys = []
        for row in rows:
            keys.append(row[0])
    # get population sum
    pop_table = get_table(table_name)
    if pop_table is None:
        return [], []
    if len(keys) == 0:
        return [], []
    age_sum = getattr(pop_table.c, keys[0])
    for key in keys[1:]:
        age_sum = age_sum + getattr(pop_table.c, key)
    if query is not None and indices is not None:
        query_wkb = from_shape(query, srid=4326)
        where_clause = pop_table.c.pid.in_(indices) | pop_table.c.geometry.ST_Within(query_wkb)
    elif query is not None:
        query_wkb = from_shape(query, srid=4326)
        where_clause = pop_table.c.geometry.ST_Within(query_wkb)
    else:
        if indices is None:
            raise ValueError("This should not happen.")
        where_clause = pop_table.c.pid.in_(indices)
    stmt = select(pop_table.c.pid, pop_table.c.x, pop_table.c.y, age_sum).where(where_clause)
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    if indices is not None:
        for row in rows:
            index = int(row[0])
            if index in index_mapping:
                i = index_mapping[index]
                locations[i] = (row[1], row[2])
                weights[i] = row[3]
            else:
                locations.append((row[1], row[2]))
                weights.append(row[3])
    else:
        for row in rows:
            locations.append((row[1], row[2]))
            weights.append(row[3])
    return locations, weights

async def get_population_geometry(session: AsyncSession, query: Polygon, typ: str = 'standard_all') -> tuple[list[int], list[tuple[float, float]]]:
    """Returns list of population grid-cell indices and list of population locations.

    Args:
        session: database session
        query: query extent
        typ: population type (e.g. standard, kita_schul)

    Returns:
        indices: list of population grid-cell indices (can be used in calls to "get_population_values")
        utm_locations: list of population locations (centroid of cell in utm32 coordinate system)

    Note:
        - this function currently returns locations as points in utm32 as they are directly stored in db tables
        - future versions might return grid-cell geometry (instead of centroid) and take an optional crs parameter to define the crs of the returned geometry
    """
    indices: list[int] = []
    utm_locations: list[tuple[float, float]] = []

    query_wkb = from_shape(query, srid=4326)

    list_table = get_table("population_list")
    if list_table is None:
        return indices, utm_locations
    # get population name
    name = typ
    if typ == "standard_all":
        name = "standard"
    # get population tables
    stmt = select(list_table.c.table_name, list_table.c.meta_table_name).where(list_table.c.name == name)
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    table_name = None
    meta_table_name = None
    for row in rows:
        table_name = row[0]
        meta_table_name = row[1]
    if table_name is None or meta_table_name is None:
        return indices, utm_locations
    # get population sum
    pop_table = get_table(table_name)
    if pop_table is None:
        return indices, utm_locations
    stmt = select(pop_table.c.pid, pop_table.c.utm_x, pop_table.c.utm_y).where(pop_table.c.geometry.ST_Within(query_wkb))
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    for row in rows:
        indices.append(row[0])
        utm_locations.append((row[1], row[2]))
    return indices, utm_locations

async def get_available_population(session: AsyncSession) -> dict:
    """Returns a list of available population types.

    Args:
        session: database session

    Returns:
        list of available population types (as expected by dva-fe)
    """
    populations = {}
    list_table = get_table("population_list")
    if list_table is None:
        return populations
    stmt = select(list_table.c.name, list_table.c.i18n_key, list_table.c.meta_table_name).where()
    rows = await session.execute(stmt)
    rows = rows.fetchall()
    for row in rows:
        name = str(row[0])
        i18n_key = str(row[1])
        meta_table_name = str(row[2])
        populations[name] = {"text": i18n_key, "items": meta_table_name}
    for group in populations:
        meta_table_name = populations[group]["items"]
        meta_table = get_table(meta_table_name)
        if meta_table is None:
            continue
        stmt = select(meta_table.c.age_group_key, meta_table.c.from_, meta_table.c.to_).where()
        rows = await session.execute(stmt)
        rows = rows.fetchall()
        ages = {}
        for row in rows:
            age_group_key = str(row[0])
            from_age = int(row[1])
            to_age = int(row[2])
            if to_age < 0:
                age_range = (from_age,)
            else:
                age_range = (from_age, to_age)
            ages[age_group_key] = age_range
        populations[group]["items"] = ages
    return populations
