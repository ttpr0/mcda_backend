# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import pyaccess

base = pyaccess.load_graph_base("./files/graphs/base")
weight = pyaccess.load_edge_weights("./files/graphs/weight")

GRAPH = pyaccess.build_base_graph(base, weight)

async def calcFCA(population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], max_range: float, mode: str) -> list[float]:
    global GRAPH
    dem_points = pyaccess.CoordVector()
    dem_weights = pyaccess.IntVector()
    sup_points = pyaccess.CoordVector()
    sup_weights = pyaccess.IntVector()
    for i in range(len(population_locations)):
        lon, lat = population_locations[i]
        weight = population_weights[i]
        dem_points.append((lon, lat))
        dem_weights.append(int(weight))
    for i in range(len(facility_locations)):
        lon, lat = facility_locations[i]
        weight = facility_weights[i]
        sup_points.append((lon, lat))
        sup_weights.append(int(weight))

    decay = pyaccess.LinearDecay(int(max_range))

    match mode:
        case "isochrones":
            access = pyaccess.calc_dijkstra_2sfca(GRAPH, dem_points, dem_weights, sup_points, sup_weights, decay)
        case "isoraster":
            access = pyaccess.calc_dijkstra_2sfca(GRAPH, dem_points, dem_weights, sup_points, sup_weights, decay)
        case "matrix":
            access = pyaccess.calc_dijkstra_2sfca(GRAPH, dem_points, dem_weights, sup_points, sup_weights, decay)
        case _:
            access = pyaccess.calc_dijkstra_2sfca(GRAPH, dem_points, dem_weights, sup_points, sup_weights, decay)
    return access

async def calcRange(population_locations: list[tuple[float, float]], facility_location: tuple[float, float], max_range: int, mode:str) -> list[int]:
    global GRAPH
    dem_points = pyaccess.CoordVector()
    sup_point = pyaccess.Coord()
    sup_point.lon = facility_location[0]
    sup_point.lat = facility_location[1]
    for i in range(len(population_locations)):
        lon, lat = population_locations[i]
        dem_points.append((lon, lat))
    match mode:
        case "isochrones":
            access = pyaccess.calc_range_dijkstra(GRAPH, sup_point, dem_points, max_range)
        case "isoraster":
            access = pyaccess.calc_range_dijkstra(GRAPH, sup_point, dem_points, max_range)
        case "matrix":
            access = pyaccess.calc_range_dijkstra(GRAPH, sup_point, dem_points, max_range)
        case _:
            access = pyaccess.calc_range_dijkstra(GRAPH, sup_point, dem_points, max_range)
    return access
