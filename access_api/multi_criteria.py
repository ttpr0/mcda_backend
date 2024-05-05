# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import numpy as np
import pyaccess

import config
from . import PROFILES


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

async def calcMultiCriteria2(population_locations: list[tuple[float, float]], population_weights: list[int], infrastructures: dict[str, Infrastructure]) -> dict[str, list[float]]:
    global PROFILES
    profile = PROFILES.get_profile("driving-car")
    if profile is None:
        raise ValueError("Invalid profile.")
    access = {}
    access["multiCriteria"] = [0] * len(population_locations)
    weight_sum = sum([i.weight for i in infrastructures.values()])
    for name, infra in infrastructures.items():
        decay = pyaccess.hybrid_decay([int(i) for i in infra.ranges], infra.range_factors)
        # decay = pyaccess.linear_decay(int(infra.ranges[-1]))
        reach = profile.calc_reachability(population_locations, infra.locations, decay)
        weight = infrastructures[name].weight * 100 / weight_sum
        multi = access["multiCriteria"]
        for j in range(len(population_locations)):
            if reach[j] <= 0:
                reach[j] = -9999
                continue
            multi[j] += weight * reach[j]
        access[name] = reach.tolist()
    return access
