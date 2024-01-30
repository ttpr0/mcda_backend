# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon
from pydantic import BaseModel
import requests
import json
import asyncio
import numpy as np

import config
from .reachability import calcReachability


class Infrastructure():
    weight: float
    ranges: list[float]
    range_factors: list[float]
    locations: list[tuple[float, float]]
    weights: list[float]

    def __init__(self, weight: float, ranges: list[float], range_factors: list[float], locations: list[tuple[float, float]], weights: list[float]):
        self.weight = weight
        self.ranges = ranges
        self.range_factors = range_factors
        self.locations = locations
        self.weights = weights        


async def calcMultiCriteria(population_locations: list[tuple[float, float]], population_weights: list[int], infrastructures: dict[str, Infrastructure]) -> dict[str, list[float]]:
    tasks: list[asyncio.Task] = []
    weight_sum = 0
    names = []
    for name, infra in infrastructures.items():
        tasks.append(asyncio.create_task(calcReachability(population_locations, population_weights, infra.locations, infra.weights, infra.ranges, infra.range_factors)))
        names.append(name)
        weight_sum += infra.weight

    results = await asyncio.gather(*tasks)

    accessibilities: dict[str, list[float]] = {}
    multi: list[float] = [0] * len(population_locations)
    for i, arr in enumerate(await asyncio.gather(*tasks)):
        name = names[i]
        weight = infrastructures[name].weight / weight_sum
        for j in range(len(arr)):
            if arr[j] < 0:
                continue
            multi[j] += weight * arr[j]
        accessibilities[name] = arr
    if multi is not None:
        accessibilities["multiCriteria"] = multi

    return accessibilities

async def calcMultiCriteria2(population_locations: list[tuple[float, float]], population_weights: list[int], infrastructures: dict[str, Infrastructure]) -> dict[str, list[float]]:
    infras = {}
    for name, obj in infrastructures.items():
        infras[name] = {
            "infrastructure_weight": obj.weight,
            "supply": {
                "supply_locations": obj.locations,
                "supply_weights": obj.weights,
            },
            "decay": {
                "decay_type": "hybrid",
                "ranges": obj.ranges,
                "range_factors": obj.range_factors
            },
        }
    header = {'Content-Type': 'application/json'}
    body = {
        "infrastructures": infras,
        "demand": {
            "demand_locations": population_locations,
            "demand_weights": population_weights,
        },
        "routing": {
            "profile": "driving-car",
            "range_type": "time",
            "location_type": "destination",
            "isochrone_smoothing": 5
        },
        "response": {
            "scale": True,
            "scale_range": [0, 100],
            "no_data_value": -9999,
        },
        "return_all": True,
        "return_weighted": False,
    }
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/multicriteria/multi", json=body, headers=header))
    accessibilities = response.json()
    return accessibilities["access"]
