# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon
import requests
import json
import asyncio
import numpy as np
import random
import base64

import config


async def calcNearestQuery(population_locations: list[tuple[float, float]], population_weights: list[int], envelop: tuple[float, float, float, float], facilities: list[tuple[float, float]], facility_weights: list[float], ranges: list[float]) -> np.ndarray:
    header = {'Content-Type': 'application/json'}
    body = {
        "demand": {
            "demand_locations": population_locations,
            "envelop": envelop,
        },
        "supply": {
            "supply_locations": facilities,
            "supply_weights": facility_weights,
        },
        "facility_count": 3,
        "range_type": "discrete",
        "ranges": ranges,
        "compute_type": "mean",
    }
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/queries/n_nearest", json=body, headers=header))
    accessibilities = response.json()
    arr: np.ndarray = np.array(accessibilities["result"])
    return arr


async def calcNearestQuery2(population_locations: list[tuple[float, float]], envelop: tuple[float, float, float, float], facilities: list[tuple[float, float]], facility_weights: list[float], ranges: list[float], facility_count: int, compute_type: str) -> tuple[list[float], str]:
    header = {'Content-Type': 'application/json'}
    body = {
        "demand": {
            "demand_locations": population_locations,
            "envelop": envelop,
        },
        "supply": {
            "supply_locations": facilities,
            "supply_weights": facility_weights,
        },
        "facility_count": facility_count,
        "range_type": "discrete",
        "ranges": ranges,
        "compute_type": compute_type,
    }
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/queries/n_nearest", json=body, headers=header))
    accessibilities = response.json()
    return accessibilities["result"], accessibilities["session_id"]


async def calcNearestQuery3(query_id: str, facility_weights: list[float], facility_count: int, compute_type: str) -> tuple[list[float], str]:
    header = {'Content-Type': 'application/json'}
    body = {
        "session_id": query_id,
        "supply": {
            "supply_weights": facility_weights,
        },
        "facility_count": facility_count,
        "compute_type": compute_type,
    }
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/queries/n_nearest", json=body, headers=header))
    accessibilities = response.json()
    return accessibilities["result"], accessibilities["session_id"]
