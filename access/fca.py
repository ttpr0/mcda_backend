# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon
import requests
import json
import asyncio
import time
import numpy as np

import config


async def calcFCA(population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], ranges: list[float], range_factors: list[float], mode: str = "isochrones", travel_mode: str = "driving-car") -> np.ndarray:
    header = {'Content-Type': 'application/json'}
    body = {
        "ranges": ranges,
        "facility_locations": facility_locations,
        "facility_capacities": facility_weights,
        "population": {
            "population_locations": population_locations,
            "population_weights": population_weights,
        },
        "distance_decay": {
            "decay_type": "hybrid",
            "ranges": ranges,
            "range_factors": range_factors
        },
        "routing": {
            "profile": travel_mode,
            "range_type": "time",
            "location_type": "destination",
            "isochrone_smoothing": 5
        },
        "mode": mode,
    }
    loop = asyncio.get_running_loop()
    data = json.dumps(body)
    t1 = time.time()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/fca", data=data, headers=header))
    t2 = time.time()
    print(f"time: {t2-t1}")
    accessibilities = response.json()
    arr: np.ndarray = np.array(accessibilities["access"])
    return arr


async def calcFCA2(population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], max_range: float) -> np.ndarray:
    header = {'Content-Type': 'application/json'}
    body = {
        "facility_locations": facility_locations,
        "facility_capacities": facility_weights,
        "population_locations": population_locations,
        "population_weights": population_weights,
        "max_range": max_range,
    }
    loop = asyncio.get_running_loop()
    data = json.dumps(body)
    t1 = time.time()
    response = await loop.run_in_executor(None, lambda: requests.post("http://172.26.62.41:5002/v0/fca", data=data, headers=header))
    t2 = time.time()
    print(f"time: {t2-t1}")
    accessibilities = response.json()
    arr: np.ndarray = np.array(accessibilities["access"])
    return arr