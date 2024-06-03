# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from shapely import contains_xy
import asyncio
import time
from typing import Annotated

from models.population import get_population
from models.physicians import get_physicians
from models.planning_areas import get_planning_area
from models.travel_modes import get_distance_decay, is_valid_travel_mode, get_default_travel_mode
from helpers.util import get_extent
from filters.user import get_current_user, User
from services.method import get_method_service, IMethodService, Infrastructure


ROUTER = APIRouter()

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

@ROUTER.post("/grid")
async def spatial_access_api(
        req: SpatialAccessRequest,
        method_service: Annotated[IMethodService, Depends(get_method_service)],
        user: Annotated[User, Depends(get_current_user)]
    ):
    query = get_planning_area(req.planning_area)
    if query is None:
        return {"error": "invalid request"}
    buffer_query = query.buffer(0.2)

    t1 = time.time()
    if req.population_indizes is None:
        points, utm_points, weights = get_population(buffer_query)
    else:
        points, utm_points, weights = get_population(buffer_query, req.population_type, req.population_indizes)
    t2 = time.time()
    print(f"time to load population: {t2-t1}")
    facility_points, facility_weights = get_physicians(buffer_query, req.facility_type, req.facility_capacity)
    distance_decay = get_distance_decay(req.travel_mode, req.decay_type, req.supply_level, req.facility_type)
    travel_mode = req.travel_mode
    if not is_valid_travel_mode(travel_mode):
        travel_mode = get_default_travel_mode()

    task = asyncio.create_task(method_service.calcFCA(
        points, weights, facility_points, facility_weights, distance_decay, travel_mode))

    minx, miny, maxx, maxy = get_extent(utm_points)
    extend = (minx-50, miny-50, maxx+50, maxy+50)
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

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
            "coordinates": [p[0], p[1]],
            "properties": {
                "accessibility": access,
            }
        })

    return {"features": features, "crs": crs, "extend": extend, "size": size, "min": min_val, "max": max_val}