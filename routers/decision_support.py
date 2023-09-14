# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter
from pydantic import BaseModel
from shapely import Point, Polygon, contains_xy
from typing import Any
import asyncio
import numpy as np

import config

from helpers.population import get_population, convert_population_keys
from helpers.facilities import get_facility
from helpers.util import get_extent
from helpers.responses import GridFeature
from access.multi_criteria import calcMultiCriteria, calcMultiCriteria2
from access.reachability import calcReachability
from access.oas_population import store_population, request_population


router = APIRouter()

class InfrastructureParams(BaseModel):
    infrastructure_weight: float
    ranges: list[float]
    range_factors: list[float]
    facility_type: str

class MultiCriteriaRequest(BaseModel):
    # infrastructure parameters
    infrastructures: dict[str, InfrastructureParams]
    # query extent
    envelop: tuple[float, float, float, float]
    # population parameters
    population_type: str
    population_indizes: list[str]|None


@router.post("/grid")
async def multi_api(req: MultiCriteriaRequest):
    ll = (req.envelop[0], req.envelop[1])
    ur = (req.envelop[2], req.envelop[3])
    query = Polygon(((ll[0], ll[1]), (ll[0], ur[1]), (ur[0], ur[1]), (ur[0], ll[1])))
    buffer_query = query.buffer(0.2)
    if req.population_indizes is None or req.population_type is None:
        population_locations, utm_points, population_weights = get_population(query)
    else:
        indizes = convert_population_keys(req.population_type, req.population_indizes)
        if indizes is None:
            return {"error": "invalid population indizes"}
        population_locations, utm_points, population_weights = get_population(query, req.population_type, indizes)
    population_id = await store_population(population_locations, population_weights)

    tasks: list[asyncio.Task] = []
    weight_sum = 0
    names = []
    for name, param in req.infrastructures.items():
        facility_points, facility_weights = get_facility(param.facility_type, buffer_query)
        tasks.append(asyncio.create_task(calcReachability(population_id, facility_points, facility_weights, param.ranges, param.range_factors)))
        names.append(name)
        weight_sum += param.infrastructure_weight

    features: list[GridFeature] = []
    minx, miny, maxx, maxy = get_extent(utm_points)

    for p in utm_points:
        features.append(GridFeature(p[0], p[1], {}))

    results = await asyncio.gather(*tasks)

    accessibilities: dict[str, list[float]] = {}
    multi: list[float] = [0] * len(utm_points)
    for i, arr in enumerate(await asyncio.gather(*tasks)):
        name = names[i]
        weight = req.infrastructures[name].infrastructure_weight / weight_sum
        for j in range(len(arr)):
            if arr[j] < 0:
                continue
            multi[j] += weight * arr[j]
        accessibilities[name] = arr
    if multi is not None:
        accessibilities["multiCritera"] = multi

    for name, array in accessibilities.items():
        for i, _ in enumerate(utm_points):
            feature = features[i]
            access: float = float(array[i])
            feature.value[name] = access
            if population_weights[i] == 0 or access == -9999:
                feature.value[name + "_weighted"] = -9999
            else:
                feature.value[name + "_weighted"] = access / population_weights[i]

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    return {"features": features, "crs": crs, "extend": extend, "size": size}

# @router.post("/grid2")
# async def multi_api2(req: MultiCriteriaRequest):
#     ll = (req.envelop[0], req.envelop[1])
#     ur = (req.envelop[2], req.envelop[3])
#     query = Polygon(((ll[0], ll[1]), (ll[0], ur[1]), (ur[0], ur[1]), (ur[0], ll[1])))
#     if req.population_indizes is None or req.population_type is None:
#         population_locations, utm_points, population_weights = get_population(query)
#     else:
#         population_locations, utm_points, population_weights = get_population(query, req.population_type, req.population_indizes)
#     population_id = await store_population(population_locations, population_weights)

#     task = asyncio.create_task(calcMultiCriteria2(population_locations, population_weights, req.infrastructures))

#     features: list[GridFeature] = []
#     minx, miny, maxx, maxy = get_extent(utm_points)

#     for p in utm_points:
#         features.append(GridFeature(p[0], p[1], {}))

#     accessibilities = await task
#     for i, _ in enumerate(utm_points):
#         feature = features[i]
#         access = accessibilities[i]
#         feature.value = access

#     extend = [minx-50, miny-50, maxx+50, maxy+50]
#     dx = extend[2] - extend[0]
#     dy = extend[3] - extend[1]
#     size = [int(dx/100), int(dy/100)]

#     crs = "EPSG:25832"

#     return {"features": features, "crs": crs, "extend": extend, "size": size}