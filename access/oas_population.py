# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon
from pydantic import BaseModel
import requests
import json
import asyncio
import numpy as np

import config


async def store_population(locations: list[tuple[float, float]], weights: list[int]) -> str:
    # store population and retrive id
    header = {'Content-Type': 'application/json'}
    body = {
        "population": {
            "demand_locations": locations,
            "demand_weights": weights,
        }
    }
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/utility/population/store", json=body, headers=header))
    resp = response.json()
    population_id = resp["id"]
    return population_id


async def request_population(envelop: tuple[float, float, float, float]) -> tuple[str, list[tuple[float, float]], list[float]]:
    # store population and retrive id
    header = {'Content-Type': 'application/json'}
    body = {
        "population": {
            "envelop": envelop
        }
    }
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/utility/population/store", json=body, headers=header))
    resp = response.json()
    population_id = resp["id"]

    # get points and weights from stored population
    header = {'Content-Type': 'application/json'}
    body = {
        "population_id": population_id
    }
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/utility/population/get", json=body, headers=header))
    resp = response.json()
    population_locations = resp["locations"]
    population_weights = resp["weights"]
    return population_id, population_locations, population_weights
