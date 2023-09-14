# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon
import requests
import json
import asyncio
import numpy as np
import random
import base64

import config


async def calcAggregateQuery(population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], max_range: float, compute_type: str) -> list[float]:
    header = {'Content-Type': 'application/json'}
    body = {
        "demand": {
            "demand_locations": population_locations,
            "demand_weights": population_weights,
        },
        "supply": {
            "supply_locations": facility_locations,
            "supply_weights": facility_weights,
        },
        "range": max_range,
        "compute_type": compute_type,
    }
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/queries/aggregate", json=body, headers=header))
    accessibilities = response.json()
    arr: list[float] = accessibilities["result"]
    return arr
