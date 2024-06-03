# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import asyncio
import json
import requests
from fastapi import HTTPException, status

from .util import Infrastructure

class OASMethodService:
    _oas_url: str

    def __init__(self, oas_url: str):
        self._oas_url = oas_url

    async def calcFCA(self, population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], decay: dict, travel_mode: str = "driving-car") -> list[float]:
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
            "distance_decay": decay,
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
        }
        loop = asyncio.get_running_loop()
        data = json.dumps(body)
        response = await loop.run_in_executor(None, lambda: requests.post(self._oas_url + "/v1/accessibility/enhanced_2sfca", data=data, headers=header))
        accessibilities = response.json()
        arr: list[float] = accessibilities["access"]
        return arr

    async def calcMultiCriteria(self, population_locations: list[tuple[float, float]], population_weights: list[int], infrastructures: dict[str, Infrastructure], travel_mode: str = "driving-car") -> tuple[dict[str, list[float]], dict[str, list[int]]]:
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
                "profile": travel_mode,
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
        response = await loop.run_in_executor(None, lambda: requests.post(self._oas_url + "/v1/multicriteria/multi", json=body, headers=header))
        accessibilities = response.json()
        return accessibilities["access"]

    async def calcSetCoverage(self, population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], max_range: int, percent_coverage: float, travel_mode: str = "driving-car") -> list[bool]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This Method is not implemented")
