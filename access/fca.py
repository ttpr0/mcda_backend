# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon
import requests
import json
import asyncio
import time
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
        "mode": mode,
    }
    loop = asyncio.get_running_loop()
    data = json.dumps(body)
    t1 = time.time()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/accessibility/fca", data=data, headers=header))
    t2 = time.time()
    print(f"time: {t2-t1}")
    accessibilities = response.json()
    arr: list[float] = accessibilities["access"]
    return arr


async def calcFCA2(envelop: tuple[float, float, float, float], facility_locations: list[tuple[float, float]], facility_weights: list[float], max_range: float) -> tuple[list[float], list[tuple[float, float]]]:
    header = {'Content-Type': 'application/json'}
    body = {
        "supply": {
            "supply_locations": facility_locations,
            "supply_weights": facility_weights,
        },
        "demand": {
            "population_name": "dvan_population",
            "envelop": envelop,
            "population_indizes": [0],
            "population_factors": [1],
        },
        "distance_decay": {
            "decay_type": "linear",
            "max_range": max_range,
        },
        "mode": "default",
        "response": {
            "scale": True,
            "scale_range": [0, 100],
            "no_data_value": -9999,
            "return_locs": True,
            "loc_crs": "EPSG:25832",
        },
    }
    loop = asyncio.get_running_loop()
    data = json.dumps(body)
    t1 = time.time()
    response = await loop.run_in_executor(None, lambda: requests.post(config.ACCESSIBILITYSERVICE_URL + "/v1/accessibility/fca", data=data, headers=header))
    t2 = time.time()
    print(f"time: {t2-t1}")
    accessibilities = response.json()
    arr: list[float] = accessibilities["access"]
    locs: list[tuple[float, float]] = accessibilities["locations"]
    return arr, locs


# from pyaccess import IntVector, CoordVector, calc_dijkstra_2sfca, load_chgraph, load_chgraph_2, Coord, calc_range_dijkstra, calc_range_phast, calc_range_phast_2, calc_dijkstra_2sfca_2, calc_range_rphast_2sfca, calc_range_rphast_2sfca2

# GRAPH = load_chgraph("./files/graphs/bench_ch")
# GRAPH2 = load_chgraph_2("./files/graphs/bench_ch_2")

async def calcFCA3(population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], max_range: float, mode: str) -> list[float]:
    # global GRAPH
    # dem_points = CoordVector()
    # dem_weights = IntVector()
    # sup_points = CoordVector()
    # sup_weights = IntVector()
    # for i in range(len(population_locations)):
    #     lon, lat = population_locations[i]
    #     weight = population_weights[i]
    #     dem_points.append((lon, lat))
    #     dem_weights.append(int(weight))
    # for i in range(len(facility_locations)):
    #     lon, lat = facility_locations[i]
    #     weight = facility_weights[i]
    #     sup_points.append((lon, lat))
    #     sup_weights.append(int(weight))

    # match mode:
    #     case "isochrones":
    #         access = calc_dijkstra_2sfca(GRAPH, dem_points, dem_weights, sup_points, sup_weights, int(max_range))
    #     case "isoraster":
    #         access = calc_range_rphast_2sfca(GRAPH, dem_points, dem_weights, sup_points, sup_weights, int(max_range))
    #     case "matrix":
    #         access = calc_range_rphast_2sfca2(GRAPH, dem_points, dem_weights, sup_points, sup_weights, int(max_range))
    #     case _:
    #         access = calc_dijkstra_2sfca_2(GRAPH, dem_points, dem_weights, sup_points, sup_weights, int(max_range))
    # return access
    pass

async def calcRange(population_locations: list[tuple[float, float]], facility_location: tuple[float, float], max_range: int, mode:str) -> list[int]:
    # global GRAPH
    # dem_points = CoordVector()
    # sup_point = Coord()
    # sup_point.lon = facility_location[0]
    # sup_point.lat = facility_location[1]
    # for i in range(len(population_locations)):
    #     lon, lat = population_locations[i]
    #     dem_points.append((lon, lat))
    # match mode:
    #     case "isochrones":
    #         access = calc_range_dijkstra(GRAPH, sup_point, dem_points, max_range)
    #     case "isoraster":
    #         access = calc_range_phast(GRAPH, sup_point, dem_points, max_range)
    #     case "matrix":
    #         access = calc_range_phast_2(GRAPH, sup_point, dem_points, max_range)
    #     case _:
    #         access = calc_range_dijkstra(GRAPH, sup_point, dem_points, max_range)
    # return access
    pass