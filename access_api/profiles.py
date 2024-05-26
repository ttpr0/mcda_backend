# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from enum import Enum
from typing import Protocol
import numpy as np
import pyaccess

import config

class IRoutingProfile(Protocol):
    def calc_reachability(self, dem_points: list[tuple[float, float]], sup_points: list[tuple[float, float]], decay: pyaccess._pyaccess_ext.IDistanceDecay) -> tuple[np.ndarray, np.ndarray]:
        ...

    def calc_set_coverage(self, dem_points: list[tuple[float, float]], dem_weights: list[int], sup_points: list[tuple[float, float]], max_range: int, percent_coverage: float) -> np.ndarray:
        ...

    def calc_2sfca(self, dem_points: list[tuple[float, float]], dem_weights: list[int], sup_points: list[tuple[float, float]], sup_weights: list[int], decay: pyaccess._pyaccess_ext.IDistanceDecay) -> np.ndarray:
        ...

class RoutingProfile:
    _graph: pyaccess.Graph
    _weight: str

    def __init__(self, graph: pyaccess.Graph, _weight: str):
        self._graph = graph
        self._weight = _weight

    def calc_reachability(self, dem_points: list[tuple[float, float]], sup_points: list[tuple[float, float]], decay: pyaccess._pyaccess_ext.IDistanceDecay) -> tuple[np.ndarray, np.ndarray]:
        return pyaccess.calc_reachability_2(self._graph, dem_points, sup_points, decay, weight=self._weight)
    
    def calc_set_coverage(self, dem_points: list[tuple[float, float]], dem_weights: list[int], sup_points: list[tuple[float, float]], max_range: int, percent_coverage: float) -> np.ndarray:
        return pyaccess.weighted_set_coverage(self._graph, dem_points, dem_weights, sup_points, percent_coverage, max_range, weight=self._weight)

    def calc_2sfca(self, dem_points: list[tuple[float, float]], dem_weights: list[int], sup_points: list[tuple[float, float]], sup_weights: list[int], decay: pyaccess._pyaccess_ext.IDistanceDecay) -> np.ndarray:
        return pyaccess.calc_2sfca(self._graph, dem_points, dem_weights, sup_points, sup_weights, decay, weight=self._weight)

class TransitProfile:
    _graph: pyaccess.Graph
    _weekday: str
    _min_departure: int
    _max_departure: int

    def __init__(self, graph: pyaccess.Graph, weekday: str, min_departure: int, max_departure: int):
        self._graph = graph
        self._weekday = weekday
        self._min_departure = min_departure
        self._max_departure = max_departure

    def calc_reachability(self, dem_points: list[tuple[float, float]], sup_points: list[tuple[float, float]], decay: pyaccess._pyaccess_ext.IDistanceDecay) -> tuple[np.ndarray, np.ndarray]:
        return pyaccess.calc_reachability_2(self._graph, dem_points, sup_points, decay=decay, transit="transit", transit_weight=self._weekday, min_departure=self._min_departure, max_departure=self._max_departure)

    def calc_set_coverage(self, dem_points: list[tuple[float, float]], dem_weights: list[int], sup_points: list[tuple[float, float]], max_range: int, percent_coverage: float) -> np.ndarray:
        return pyaccess.weighted_set_coverage(self._graph, dem_points, dem_weights, sup_points, percent_coverage, max_range, transit="transit", transit_weight=self._weekday, min_departure=self._min_departure, max_departure=self._max_departure)

    def calc_2sfca(self, dem_points: list[tuple[float, float]], dem_weights: list[int], sup_points: list[tuple[float, float]], sup_weights: list[int], decay: pyaccess._pyaccess_ext.IDistanceDecay) -> np.ndarray:
        return pyaccess.calc_2sfca(self._graph, dem_points, dem_weights, sup_points, sup_weights, decay=decay, transit="transit", transit_weight=self._weekday, min_departure=self._min_departure, max_departure=self._max_departure)

class Profile:
    _weights: list[str]

    def __init__(self, weights):
        self._weights = weights

class ProfileManager:
    _graphs: dict[str, pyaccess.Graph]
    _profiles: dict[str, Profile]

    def __init__(self):
        self._graphs = {}
        self._profiles = {}

    def add_profile(self, name: str, graph: pyaccess.Graph, weights: list[str]):
        self._graphs[name] = graph
        self._profiles[name] = Profile(weights)

    def has_profile(self, name: str) -> bool:
        return name in self._profiles

    def get_profile(self, profile: str, weight: str = "time", weekday: str = "wednesday", timespan: tuple[int , int]= (28800, 36000)) -> IRoutingProfile | None:
        graph = self._graphs[profile]
        params = self._profiles[profile]
        if weight not in params._weights:
            raise Exception(f"Weight {weight} not found in profile {profile}")
        match profile:
            case "driving-car" | "walking-foot":
                return RoutingProfile(graph, weight)
            case "public-transit":
                return TransitProfile(graph, weekday, timespan[0], timespan[1])
            case _:
                return None

def build_driving_car(store: bool = True) -> pyaccess.Graph:
    nodes, edges = pyaccess.parse_osm(config.GRAPH_OSM_FILE, "driving")
    graph = pyaccess.new_graph(nodes, edges)
    # optimize graph
    unconnected = pyaccess.calc_unconnected_nodes(graph)
    graph.remove_nodes(unconnected)
    pyaccess.util.remove_graph_nodes(nodes, edges, unconnected)
    ordering = pyaccess.calc_dfs_ordering(graph)
    graph.reorder_nodes(ordering)
    pyaccess.util.reorder_graph_data(nodes, edges, ordering)
    # build weighting
    weight = pyaccess.build_fastest_weighting(graph, edges)
    graph.add_weighting("time", weight)
    # store graph
    if store:
        graph.store("driving-car", config.GRAPH_DIR)
        nodes.to_feather(f"{config.GRAPH_DIR}/driving-car-nodes")
        edges.to_feather(f"{config.GRAPH_DIR}/driving-car-edges")
    return graph

def build_walking_foot(store: bool = True) -> pyaccess.Graph:
    nodes, edges = pyaccess.parse_osm(config.GRAPH_OSM_FILE, "walking")
    graph = pyaccess.new_graph(nodes, edges)
    # optimize graph
    unconnected = pyaccess.calc_unconnected_nodes(graph)
    graph.remove_nodes(unconnected)
    pyaccess.util.remove_graph_nodes(nodes, edges, unconnected)
    ordering = pyaccess.calc_dfs_ordering(graph)
    graph.reorder_nodes(ordering)
    pyaccess.util.reorder_graph_data(nodes, edges, ordering)
    # build weighting
    weight = pyaccess.build_fastest_weighting(graph, edges)
    graph.add_weighting("time", weight)
    # store graph
    if store:
        graph.store("walking-foot", config.GRAPH_DIR)
        nodes.to_feather(f"{config.GRAPH_DIR}/walking-foot-nodes")
        edges.to_feather(f"{config.GRAPH_DIR}/walking-foot-edges")
    return graph

def build_public_transit(graph: pyaccess.Graph, store: bool = True) -> pyaccess.Graph:
    stops, conns, schedules = pyaccess.parse_gtfs(config.GRAPH_GTFS_DIR, config.GRAPH_GTFS_FILTER_POLYGON)
    graph.add_public_transit("transit", stops, conns, weight="time")
    for day, schedule in schedules.items():
        weight = pyaccess.new_transit_weighting(graph, "transit")
        for i, conn in enumerate(schedule):
            weight.set_connection_schedule(i, conn)
        graph.add_transit_weighting(day, weight, "transit")
    if store:
        graph.store()
    return graph

def load_or_create_profiles() -> ProfileManager:
    profile_manager = ProfileManager()
    # load or create profiles
    graph_cache: dict[str, pyaccess.Graph] = {}
    for profile in config.ROUTING_PROFILES:
        if profile_manager.has_profile(profile):
            continue
        try:
            match profile:
                case "public-transit":
                    graph_name = "walking-foot"
                case _:
                    graph_name = profile
            if graph_name in graph_cache:
                graph = graph_cache[graph_name]
            else:
                graph = pyaccess.load_graph(graph_name, config.GRAPH_DIR)
                graph_cache[graph_name] = graph
            if profile == "public-transit":
                if not graph.has_public_transit("transit"):
                    raise ValueError("")
            profile_manager.add_profile(profile, graph, ["time"])
        except:
            match profile:
                case "driving-car":
                    graph = build_driving_car()
                    graph_cache["driving-car"] = graph
                case "walking-foot":
                    graph = build_walking_foot()
                    graph_cache["walking-foot"] = graph
                case "public-transit":
                    if "walking-foot" in graph_cache:
                        graph = graph_cache["walking-foot"]
                    else:
                        graph = build_walking_foot()
                        graph_cache["walking-foot"] = graph
                    graph = build_public_transit(graph)
            profile_manager.add_profile(profile, graph, ["time"])
    return profile_manager
