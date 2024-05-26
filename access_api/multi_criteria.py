# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import numpy as np
import pyaccess

import config
from . import PROFILES
from .decay import get_distance_decay


class Infrastructure():
    weight: float
    decay: dict
    cutoffs: list[int]
    locations: list[tuple[float, float]]
    weights: list[float]

    def __init__(self, weight: float, decay: dict, cutoffs: list[int], locations: list[tuple[float, float]], weights: list[float]):
        self.weight = weight
        self.decay = decay
        self.cutoffs = cutoffs
        self.locations = locations
        self.weights = weights        

async def calcMultiCriteria(population_locations: list[tuple[float, float]], population_weights: list[int], infrastructures: dict[str, Infrastructure], travel_mode: str = "driving-car") -> tuple[dict[str, list[float]], dict[str, list[int]]]:
    global PROFILES
    profile = PROFILES.get_profile(travel_mode)
    if profile is None:
        raise ValueError(f"Invalid profile {travel_mode}.")
    access = {}
    access["multiCriteria"] = [0] * len(population_locations)
    counts = {}
    # weight_sum = sum([i.weight for i in infrastructures.values()])
    for name, infra in infrastructures.items():
        decay = get_distance_decay(infra.decay)
        if decay is None:
            raise ValueError(f"Invalid decay parameters {infra.decay}.")
        reach, count = profile.calc_reachability(population_locations, infra.locations, decay)
        counts[name] = count
        weight = infrastructures[name].weight
        multi = access["multiCriteria"]
        for j in range(len(population_locations)):
            if reach[j] <= 0:
                reach[j] = -9999
                continue
            multi[j] += weight * reach[j]
        access[name] = reach.tolist()
    multi = access["multiCriteria"]
    for j in range(len(population_locations)):
        if multi[j] <= 0:
            multi[j] = -9999
    return access, counts
