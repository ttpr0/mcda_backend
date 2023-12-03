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

import config
from models.population import get_population
from models.facilities import get_facility
from helpers.util import get_extent
from helpers.responses import GridFeature
from oas_api.aggregate_query import calcAggregateQuery
from oas_api.gravity import calcGravity


router = APIRouter()

class SpatialAnalysisRequest(BaseModel):
    # query extent
    envelop: tuple[float, float, float, float]
    # facility parameters
    facility_type: str
    #routing parameters
    travel_mode: str
    range_type: str
    range_max: float
    range_steps: int


@router.post("/grid")
async def spatial_analysis_api(req: SpatialAnalysisRequest):
    ll = (req.envelop[0], req.envelop[1])
    ur = (req.envelop[2], req.envelop[3])
    query = Polygon(((ll[0], ll[1]), (ll[0], ur[1]), (ur[0], ur[1]), (ur[0], ll[1])))
    population_points, utm_points, population_weights = get_population(query)
    facility_points, facility_weights = get_facility(req.facility_type, query.buffer(0.2))

    # task = asyncio.create_task(calcAggregateQuery(
    #     population_points, population_weights, facility_points, facility_weights, req.range_max, "mean"))

    ranges = []
    range_factors = []
    step_size = req.range_max / req.range_steps
    for i in range(1, req.range_steps+1):
        ranges.append(step_size*i)
        range_factors.append(1 - (step_size*i/req.range_max))
    task = asyncio.create_task(calcGravity(
        population_points, population_weights, facility_points, [], ranges, range_factors))

    features: list[GridFeature] = []
    minx, miny, maxx, maxy = get_extent(utm_points)

    accessibilities = await task
    for i, p in enumerate(utm_points):
        access: float = float(accessibilities[i])
        features.append(GridFeature(p[0], p[1], {
            "result": access,
            "population": population_weights[i]
        }))

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    return {"features": features, "crs": crs, "extend": extend, "size": size}