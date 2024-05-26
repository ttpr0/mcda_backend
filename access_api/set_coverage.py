# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import numpy as np
import pyaccess

import config
from . import PROFILES
from .decay import get_distance_decay


async def calcSetCoverage(population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], max_range: int, percent_coverage: float, travel_mode: str = "driving-car") -> list[bool]:
    global PROFILES
    profile = PROFILES.get_profile(travel_mode)
    if profile is None:
        raise ValueError(f"Invalid profile {travel_mode}.")
    arr = profile.calc_set_coverage(population_locations, population_weights, facility_locations, max_range, percent_coverage)
    return arr.tolist()
