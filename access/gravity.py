# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon
import requests
import json
import asyncio
import numpy as np

import config


async def calcGravity(population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], ranges: list[float], range_factors: list[float]) -> np.ndarray:
    header = {'Content-Type': 'application/json'}
    body = {
        "ranges": ranges,
        "range_factors": range_factors,
        "facility_locations": facility_locations,
        "facility_weights": facility_weights,
        "population": {
            "population_locations": population_locations,
            "population_weights": population_weights,
        },
    }
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/accessibility/gravity", json=body, headers=header))
    accessibilities = response.json()
    arr: np.ndarray = np.array(accessibilities["access"])
    return arr
