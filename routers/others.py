# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter
from pydantic import BaseModel
import random
import asyncio
from shapely import Polygon
from typing import Any
import numpy as np
import json
import requests

import config
from models.population import get_population
from models.facilities import get_facility
from helpers.util import get_extent
from helpers.responses import GridFeature

from oas_api.fca import calcFCA
from oas_api.n_nearest_query import calcNearestQuery
from oas_api.aggregate_query import calcAggregateQuery
from oas_api.gravity import calcGravity

router = APIRouter()


class FCARequest(BaseModel):
    ranges: list[float]
    range_factors: list[float]
    facility_locations: list[tuple[float, float]]
    mode: str
    envelop: tuple[float, float, float, float]


@router.post("/fca/grid")
async def fca_api(req: FCARequest):
    ll = (req.envelop[0], req.envelop[1])
    ur = (req.envelop[2], req.envelop[3])
    query = Polygon(((ll[0], ll[1]), (ll[0], ur[1]), (ur[0], ur[1]), (ur[0], ll[1])))
    points, utm_points, weights = get_population(query)

    # facility_weights = np.random.randint(1, 100, size=(len(req.facility_locations),)).tolist()
    facility_weights: list[float] = [1000] * len(req.facility_locations)

    task = asyncio.create_task(calcFCA(
        points, weights, req.facility_locations, facility_weights, req.ranges, req.range_factors, req.mode))

    features: list = []
    minx, miny, maxx, maxy = get_extent(utm_points)

    accessibilities = await task
    min_val = 1000000000
    max_val = -1000000000
    for i, p in enumerate(utm_points):
        access: float = accessibilities[i]
        if access >= 0:
            if access > max_val:
                max_val = access
            if access < min_val:
                min_val = access
        else:
            access = -9999
        features.append({
            "coordinates": [p[0], p[1]],
            "properties": {
                "accessibility": access,
            }
        })

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    return {"features": features, "crs": crs, "extend": extend, "size": size, "min": min_val, "max": max_val}


class NearestQueryRequest(BaseModel):
    ranges: list[float]
    facility_locations: list[tuple[float, float]]
    envelop: tuple[float, float, float, float]


@router.post("/queries/n_nearest/grid")
async def nnearest_api(req: NearestQueryRequest):
    ll = (req.envelop[0], req.envelop[1])
    ur = (req.envelop[2], req.envelop[3])
    query = Polygon(((ll[0], ll[1]), (ll[0], ur[1]), (ur[0], ur[1]), (ur[0], ll[1])))
    points, utm_points, weights = get_population(query)

    facility_weights: list[float] = [0.0] * len(req.facility_locations)
    for i in range(len(facility_weights)):
        facility_weights[i] = random.randrange(0, 100, 1)

    task = asyncio.create_task(calcNearestQuery(
        points, weights, req.envelop, req.facility_locations, facility_weights, req.ranges))

    features: list[GridFeature] = []
    minx, miny, maxx, maxy = get_extent(utm_points)

    accessibilities = await task
    for i, p in enumerate(utm_points):
        access: float = accessibilities[i]
        features.append(GridFeature(p[0], p[1], {
            "accessibility": access
        }))

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    return {"features": features, "crs": crs, "extend": extend, "size": size}


class AggregateQueryRequest(BaseModel):
    range: float
    facility_locations: list[tuple[float, float]]
    compute_type: str
    envelop: tuple[float, float, float, float]


@router.post("/queries/aggregate/grid")
async def aggregate_api(req: AggregateQueryRequest):
    ll = (req.envelop[0], req.envelop[1])
    ur = (req.envelop[2], req.envelop[3])
    query = Polygon(((ll[0], ll[1]), (ll[0], ur[1]), (ur[0], ur[1]), (ur[0], ll[1])))
    points, utm_points, weights = get_population(query)

    facility_weights: list[float] = [0.0] * len(req.facility_locations)
    for i in range(len(facility_weights)):
        facility_weights[i] = random.randrange(0, 100, 1)

    task = asyncio.create_task(calcAggregateQuery(
        points, weights, req.facility_locations, facility_weights, req.range, "MEAN"))

    features: list[GridFeature] = []
    minx, miny, maxx, maxy = get_extent(utm_points)

    accessibilities = await task
    for i, p in enumerate(utm_points):
        access: float = float(accessibilities[i])
        features.append(GridFeature(p[0], p[1], {
            "accessibility": access
        }))

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    return {"features": features, "crs": crs, "extend": extend, "size": size}


class GravityRequest(BaseModel):
    ranges: list[float]
    range_factors: list[float]
    facility_locations: list[tuple[float, float]]
    envelop: tuple[float, float, float, float]


@router.post("/accessibility/gravity/grid")
async def gravity_api(req: GravityRequest):
    ll = (req.envelop[0], req.envelop[1])
    ur = (req.envelop[2], req.envelop[3])
    query = Polygon(((ll[0], ll[1]), (ll[0], ur[1]), (ur[0], ur[1]), (ur[0], ll[1])))
    points, utm_points, weights = get_population(query)

    task = asyncio.create_task(calcGravity(
        points, weights, req.facility_locations, [], req.ranges, req.range_factors))

    features: list[GridFeature] = []
    minx, miny, maxx, maxy = get_extent(utm_points)

    accessibilities = await task
    for i, p in enumerate(utm_points):
        access: float = float(accessibilities[i])
        features.append(GridFeature(p[0], p[1], {
            "unweighted": access,
            "weighted": access / weights[i]
        }))

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    return {"features": features, "crs": crs, "extend": extend, "size": size}


class Gravity2Request(BaseModel):
    envelop: tuple[float, float, float, float]
    facility: str
    population_type: str
    population_indizes: list[int]
    ranges: list[float]
    range_factors: list[float]

@router.post("/accessibility/gravity2/grid")
async def gravity2_api(req: Gravity2Request):
    ll = (req.envelop[0], req.envelop[1])
    ur = (req.envelop[2], req.envelop[3])
    query = Polygon(((ll[0], ll[1]), (ll[0], ur[1]), (ur[0], ur[1]), (ur[0], ll[1])))
    population_points, utm_points, population_weights = get_population(query, req.population_type, req.population_indizes)
    facility_points, facility_weights = get_facility(req.facility, query.buffer(0.2))

    task = asyncio.create_task(calcGravity(
        population_points, population_weights, facility_points, [], req.ranges, req.range_factors))

    features: list[GridFeature] = []
    minx, miny, maxx, maxy = get_extent(utm_points)

    accessibilities = await task
    for i, p in enumerate(utm_points):
        access: float = float(accessibilities[i])
        features.append(GridFeature(p[0], p[1], {
            "unweighted": access,
            "weighted": access / population_weights[i]
        }))

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    return {"features": features, "crs": crs, "extend": extend, "size": size}

