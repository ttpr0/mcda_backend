# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon
from pydantic import BaseModel
import requests
import json
import asyncio
import numpy as np

import config
from .oas_population import store_population
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
    population_id = await store_population(population_locations, population_weights)

    tasks: list[asyncio.Task] = []
    weight_sum = 0
    names = []
    for name, infra in infrastructures.items():
        tasks.append(asyncio.create_task(calcReachability(population_id, infra.locations, infra.weights, infra.ranges, infra.range_factors)))
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
        accessibilities["multiCritera"] = multi

    return accessibilities
