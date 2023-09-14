# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter
from pydantic import BaseModel
from shapely import Point, Polygon, contains_xy
from typing import Any
import requests
import json
import asyncio
import time
import os
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

import config

from access.fca import calcFCA
from helpers.population import get_population, convert_population_keys
from helpers.facilities import get_facility
from helpers.physicians import get_planning_area, get_physicians
from helpers.travel_modes import get_distance_decay, is_valid_travel_mode, get_default_travel_mode
from helpers.util import get_extent
from helpers.responses import build_remote_grid, build_geoserver_grid, GridFeature


router = APIRouter()

class SpatialAccessRequest(BaseModel):
    # query extent
    supply_level: str
    planning_area: str
    # facility parameters
    facility_type: str
    facility_capacity: str
    # population parameters
    population_type: str
    population_indizes: list[str]|None
    #routing parameters
    travel_mode: str
    decay_type: str

@router.post("/grid")
async def spatial_access_api(req: SpatialAccessRequest):
    query = get_planning_area(req.supply_level, req.planning_area)
    if query is None:
        return {"error": "invalid request"}
    buffer_query = query.buffer(0.2)
    # buffer_query = query

    t1 = time.time()
    if req.population_indizes is None:
        points, utm_points, weights = get_population(buffer_query)
    else:
        indizes = convert_population_keys(req.population_type, req.population_indizes)
        if indizes is None:
            return {"error": "invalid population indizes"}
        points, utm_points, weights = get_population(buffer_query, req.population_type, indizes)
    t2 = time.time()
    print(f"time to load population: {t2-t1}")
    facility_points, facility_weights = get_physicians(buffer_query, req.supply_level, req.facility_type, req.facility_capacity)
    ranges, range_factors = get_distance_decay(req.travel_mode, req.decay_type, req.supply_level, req.facility_type)
    travel_mode = req.travel_mode
    if not is_valid_travel_mode(travel_mode):
        travel_mode = get_default_travel_mode()

    task = asyncio.create_task(calcFCA(
        points, weights, facility_points, facility_weights, ranges, range_factors, "isochrones", travel_mode))

    minx, miny, maxx, maxy = get_extent(utm_points)
    extend = (minx-50, miny-50, maxx+50, maxy+50)
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    accessibilities = await task

    features: list = []
    values = []
    min_val = 1000000000
    max_val = -1000000000
    for i, p in enumerate(utm_points):
        point = points[i]
        if not contains_xy(query, point[0], point[1]):
            continue
        access: float = float(accessibilities[i])
        if not access == -9999: 
            if access < min_val:
                min_val = access
            if access > max_val:
                max_val = access
        features.append(GridFeature(p[0], p[1], {
            "accessibility": access
        }))
        values.append((access, Point(p[0], p[1])))

    # layer_name = build_geoserver_grid(values, extend)

    return {"features": features, "crs": crs, "extend": extend, "size": size, "min": min_val, "max": max_val}

@router.post("/grid2")
async def spatial_access_api2(req: SpatialAccessRequest):
    query = get_planning_area(req.supply_level, req.planning_area)
    if query is None:
        return {"error": "invalid request"}
    buffer_query = query.buffer(0.2)
    # buffer_query = query

    t1 = time.time()
    if req.population_indizes is None:
        points, utm_points, weights = get_population(buffer_query)
    else:
        indizes = convert_population_keys(req.population_type, req.population_indizes)
        if indizes is None:
            return {"error": "invalid population indizes"}
        points, utm_points, weights = get_population(buffer_query, req.population_type, indizes)
    t2 = time.time()
    print(f"time to load population: {t2-t1}")
    facility_points, facility_weights = get_physicians(buffer_query, req.supply_level, req.facility_type, req.facility_capacity)
    ranges, range_factors = get_distance_decay(req.travel_mode, req.decay_type, req.supply_level, req.facility_type)
    travel_mode = req.travel_mode
    if not is_valid_travel_mode(travel_mode):
        travel_mode = get_default_travel_mode()

    task = asyncio.create_task(calcFCA(
        points, weights, facility_points, facility_weights, ranges, range_factors, "isochrones", travel_mode))

    minx, miny, maxx, maxy = get_extent(utm_points)
    extend = (minx-50, miny-50, maxx+50, maxy+50)
    crs = "EPSG:25832"

    accessibilities = await task

    features: list = []
    min_val = 1000000000
    max_val = -1000000000
    for i, p in enumerate(utm_points):
        point = points[i]
        if not contains_xy(query, point[0], point[1]):
            continue
        access: float = float(accessibilities[i])
        if not access == -9999: 
            if access < min_val:
                min_val = access
            if access > max_val:
                max_val = access
        features.append({
            "x": p[0],
            "y": p[1],
            "values": {
                "accessibility": access
            }
        })

    layer_id = build_remote_grid(features, extend)

    return {"url": "http://localhost:5004", "id": layer_id, "crs": crs, "extend": extend, "min": min_val, "max": max_val}