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
    decay: dict
    locations: list[tuple[float, float]]
    weights: list[float]

    def __init__(self, weight: float, decay: dict, cutoffs: list[int], locations: list[tuple[float, float]], weights: list[float]):
        self.weight = weight
        self.decay = decay
        self.locations = locations
        self.weights = weights        

async def calcMultiCriteria(population_locations: list[tuple[float, float]], population_weights: list[int], infrastructures: dict[str, Infrastructure], travel_mode: str = "driving-car") -> dict[str, list[float]]:
    infras = {}
    for name, obj in infrastructures.items():
        infras[name] = {
            "infrastructure_weight": obj.weight,
            "supply": {
                "supply_locations": obj.locations,
                "supply_weights": obj.weights,
            },
            "decay": obj.decay,
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
            "scale": False,
            "scale_range": [0, 100],
            "no_data_value": -9999,
        },
        "return_all": True,
    }
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/multicriteria/multi", json=body, headers=header))
    accessibilities = response.json()
    return accessibilities["access"]
