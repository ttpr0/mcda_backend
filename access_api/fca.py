# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import numpy as np
import pyaccess

import config
from . import PROFILES
from .decay import get_distance_decay


async def calcFCA(population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], decay: dict, travel_mode: str = "driving-car") -> list[float]:
    global PROFILES
    profile = PROFILES.get_profile(travel_mode)
    if profile is None:
        raise ValueError(f"Invalid profile {travel_mode}.")
    distance_decay = get_distance_decay(decay)
    if distance_decay is None:
        raise ValueError(f"Invalid decay parameters {decay}.")
    arr = profile.calc_2sfca(population_locations, population_weights, facility_locations, [int(i) for i in facility_weights], distance_decay)
    return arr.tolist()
