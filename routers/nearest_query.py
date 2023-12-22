# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter
from pydantic import BaseModel
from shapely import Point, Polygon
import requests
import json
import asyncio
import numpy as np
import random
import uuid

import config
from models.population import get_population
from models.facilities import get_facility
from helpers.util import get_extent
from oas_api.n_nearest_query import calcNearestQuery, calcNearestQuery2


class GridFeature:
    def __init__(self, x: float, y: float, value):
        self.x: float = x
        self.y: float = y
        self.value = value

class GridResponse:
    crs: str
    extend: list[float]
    size: list[int]
    features: list[GridFeature]

    def __init__(self, features, crs, extend, size):
        self.features = features
        self.extend = extend
        self.size = size
        self.crs = crs



class NearestQuerySession():
    query_id: str | None
    result: list[float] | None
    compute_type: str
    population_locations: list[tuple[float, float]]
    utm_locations: list[tuple[float, float]]
    facility_locations: list[tuple[float, float]]
    facility_weights: list[float]
    facility_count: int
    envelop: tuple[float, float, float, float]
    range_type: str | None
    range_max: float | None
    ranges: list[float]

    def __init__(self, 
            compute_type: str, 
            locations: list[tuple[float, float]], 
            utm_locations: list[tuple[float, float]],
            facility_locations: list[tuple[float, float]],
            facility_weights: list[float],
            facility_count: int,
            envelop: tuple[float, float, float, float],
            range_type: str | None,
            range_max: float | None,
            ranges: list[float]):
        self.query_id = None
        self.result = None
        self.compute_type = compute_type
        self.population_locations = locations
        self.utm_locations = utm_locations
        self.facility_locations = facility_locations
        self.facility_weights = facility_weights
        self.facility_count = facility_count
        self.envelop = envelop
        self.range_type = range_type
        self.range_max = range_max
        self.ranges = ranges

sessions: dict[str, NearestQuerySession] = {}

router = APIRouter()

class NearestQueryRequest(BaseModel):
    facility: str
    facility_count: int
    range_type: str | None
    range_max: float | None
    ranges: list[float]
    envelop: tuple[float, float, float, float]

class NearestQueryResultRequest(BaseModel):
    id: str

class NearestQueryComputedRequest(BaseModel):
    id: str
    compute_type: str
    range_indizes: list[int]

class NearestQueryStatisticsRequest(BaseModel):
    id: str
    envelop: tuple[float, float, float, float] | None

@router.post("")
async def getNearestQuery(req: NearestQueryRequest):
    ll = (req.envelop[0], req.envelop[1])
    ur = (req.envelop[2], req.envelop[3])
    query = Polygon(((ll[0], ll[1]), (ll[0], ur[1]), (ur[0], ur[1]), (ur[0], ll[1])))
    facility_points, facility_weights = get_facility(req.facility, query.buffer(0.2))
    population_points, utm_points, population_weights = get_population(query)

    guid = str(uuid.uuid1())

    sessions[guid] = NearestQuerySession("mean", population_points, utm_points, facility_points, facility_weights, req.facility_count, req.envelop, req.range_type, req.range_max, req.ranges)

    return {
        "status": "success",
        "query_id": guid
    }

@router.post("/result")
async def computeResult(req: NearestQueryResultRequest):
    session = sessions[req.id]

    features: list[GridFeature] = []
    minx, miny, maxx, maxy = get_extent(session.utm_locations)

    for i, p in enumerate(session.utm_locations):
        features.append(GridFeature(p[0], p[1], {
            "index": i
        }))

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    return {"features": features, "crs": crs, "extend": extend, "size": size}

@router.post("/compute")
async def computeValue(req: NearestQueryComputedRequest):
    session = sessions[req.id]

    if session.compute_type == req.compute_type and session.result is not None:
        pass
    else:
        if session.query_id is None:
            task = asyncio.create_task(calcNearestQuery2(session.population_locations, session.envelop, session.facility_locations, session.facility_weights, session.ranges, session.facility_count, req.compute_type))
            accessibilities = await task

            session.compute_type = req.compute_type
            session.result = accessibilities

    return {
        "values": session.result
    }

def in_extent(point: tuple[float, float], envelop: tuple[float, float, float, float]) -> bool:
    return point[0] > envelop[0] and point[0] < envelop[2] and point[1] > envelop[1] and point[1] < envelop[3]

@router.post("/statistics")
async def computeStatistics(req: NearestQueryStatisticsRequest):
    envelop = req.envelop
    session = sessions[req.id]

    points = session.population_locations
    results = session.result
    if results is None:
        return {"error": "no result yet computed"}

    if envelop is None:
        values = np.array([val for i, val in enumerate(results)])
    else:
        values = np.array([val for i, val in enumerate(results) if in_extent(points[i], envelop)])

    counts, _ = np.histogram(values, int(session.ranges[-1] / 60 + 1))
    return {
        "counts": counts.tolist(),
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "median": float(np.median(values)),
        "min": float(np.max(values)),
        "max": float(np.min(values))
    }