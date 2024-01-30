# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon
import requests
import json
import asyncio
import numpy as np

import config


async def calcFCA(population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], ranges: list[float], range_factors: list[float], mode: str = "isochrones", travel_mode: str = "driving-car") -> list[float]:
    header = {'Content-Type': 'application/json'}
    body = {
        "supply": {
            "supply_locations": facility_locations,
            "supply_weights": facility_weights,
        },
        "demand": {
            "demand_locations": population_locations,
            "demand_weights": population_weights,
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
        "response": {
            "scale": True,
            "scale_range": [0, 100],
            "no_data_value": -9999,
        },
        "mode": mode,
    }
    loop = asyncio.get_running_loop()
    data = json.dumps(body)
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/accessibility/enhanced_2sfca", data=data, headers=header))
    accessibilities = response.json()
    arr: list[float] = accessibilities["access"]
    return arr
