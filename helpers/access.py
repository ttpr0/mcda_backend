# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import pyaccess


GRAPH = pyaccess.load_graph("saarland", "./files/graphs")

async def calcFCA3(population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[int], max_range: float, mode: str) -> list[float]:
    global GRAPH

    decay = pyaccess.LinearDecay(int(max_range))

    match mode:
        case "isochrones":
            access = pyaccess.calc_2sfca(GRAPH, population_locations, population_weights, facility_locations, facility_weights, decay=decay, algorithm=pyaccess.OneToManyType.RANGE_DIJKSTRA)
        case "isoraster":
            access = pyaccess.calc_2sfca(GRAPH, population_locations, population_weights, facility_locations, facility_weights, decay=decay, algorithm=pyaccess.OneToManyType.RANGE_PHAST, ch="ch_1")
        case "matrix":
            access = pyaccess.calc_2sfca(GRAPH, population_locations, population_weights, facility_locations, facility_weights, decay=decay, algorithm=pyaccess.OneToManyType.RANGE_RPHAST, ch="ch_1")
        case _:
            access = pyaccess.calc_2sfca(GRAPH, population_locations, population_weights, facility_locations, facility_weights, decay=decay)
    
    return access

async def calcRange(population_locations: list[tuple[float, float]], facility_location: tuple[float, float], max_range: int, mode:str) -> list[int]:
    global GRAPH

    match mode:
        case "isochrones":
            access = pyaccess.calc_range(GRAPH, facility_location, population_locations, max_range=max_range, algorithm=pyaccess.OneToManyType.RANGE_DIJKSTRA)
        case "isoraster":
            access = pyaccess.calc_range(GRAPH, facility_location, population_locations, max_range=max_range, algorithm=pyaccess.OneToManyType.RANGE_PHAST, ch="ch_1")
        case "matrix":
            access = pyaccess.calc_range(GRAPH, facility_location, population_locations, max_range=max_range, algorithm=pyaccess.OneToManyType.RANGE_RPHAST, ch="ch_1")
        case _:
            access = pyaccess.calc_range(GRAPH, facility_location, population_locations, max_range=max_range, algorithm=pyaccess.OneToManyType.RANGE_DIJKSTRA)
    
    return access
