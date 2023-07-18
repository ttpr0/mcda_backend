# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon
from pydantic import BaseModel
import requests
import json
import asyncio
import numpy as np

import config


class InfrastructureParams(BaseModel):
    infrastructure_weight: float
    ranges: list[float]
    range_factors: list[float]
    facility_locations: list[tuple[float, float]]


async def calcMultiCriteria(population_id: str, infrastructures: dict[str, InfrastructureParams]) -> dict[str, np.ndarray]:
    multi: np.ndarray | None = None
    arrays: dict[str, np.ndarray] = {}
    
    for name, param in infrastructures.items():
        header = {'Content-Type': 'application/json'}
        body = {
            "ranges": param.ranges,
            "range_factors": param.range_factors,
            "facility_locations": param.facility_locations,
            "population": {
                "population_id": population_id,
            }
        }
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/accessibility/gravity", json=body, headers=header))
        accessibilities = response.json()
        arr: np.ndarray = np.array(accessibilities["access"])
        if multi is None:
            multi = np.zeros(arr.shape)
        multi += param.infrastructure_weight * arr
        arrays[name] = arr
    if multi is not None:
        arrays["multiCritera"] = multi
    return arrays


async def calcMultiCriteria2(population_locations: list[tuple[float, float]], population_weights: list[int], infrastructures: dict[str, InfrastructureParams]) -> list[dict[str, float]]:
    infra_params = {}
    for name, infra in infrastructures.items():
        infra_params[name] = {
            "ranges": infra.ranges,
            "range_factors": infra.range_factors,
            "infrastructure_weight": infra.infrastructure_weight,
            "facility_locations": infra.facility_locations,
        }

    header = {'Content-Type': 'application/json'}
    body = {
        "infrastructures": infra_params,
        "population": {
            "population_locations": population_locations,
            "population_weights": population_weights,
        }
    }
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/accessibility/multi", json=body, headers=header))
    accessibilities = response.json()
    return accessibilities