# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import numpy as np
import pyaccess

import config
from . import PROFILES


async def calcFCA(population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], ranges: list[float], range_factors: list[float], mode: str = "isochrones", travel_mode: str = "driving-car") -> list[float]:
    global PROFILES
    profile = PROFILES.get_profile(travel_mode)
    if profile is None:
        raise ValueError(f"Invalid profile {travel_mode}.")
    decay = pyaccess.hybrid_decay(ranges, range_factors)
    arr = profile.calc_2sfca(population_locations, population_weights, facility_locations, facility_weights, decay)
    return arr.tolist()
