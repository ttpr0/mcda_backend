# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""Module containing the actual service.
"""

from typing import Protocol
import numpy as np
import pyaccess

import config
from .routing_profile import RoutingProfile
from .transit_profile import TransitProfile
from .builders import build_driving_car, build_walking_foot, build_public_transit

class IRoutingProfile(Protocol):
    """Routing profile interface
    """
    def calc_reachability(self, dem_points: list[tuple[float, float]], sup_points: list[tuple[float, float]], decay: pyaccess._pyaccess_ext.IDistanceDecay) -> tuple[np.ndarray, np.ndarray]:
        ...

    def calc_set_coverage(self, dem_points: list[tuple[float, float]], dem_weights: list[int], sup_points: list[tuple[float, float]], max_range: int, percent_coverage: float) -> np.ndarray:
        ...

    def calc_2sfca(self, dem_points: list[tuple[float, float]], dem_weights: list[int], sup_points: list[tuple[float, float]], sup_weights: list[int], decay: pyaccess._pyaccess_ext.IDistanceDecay) -> np.ndarray:
        ...

class Profile:
    """Profile class
    """
    _weights: list[str]

    def __init__(self, weights):
        self._weights = weights

class ProfileManager:
    """Profile manager class
    """
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

def _load_or_create_profiles() -> ProfileManager:
    """Initializes the profiles from the disk or creates them from data-sources if they don't exist.
    """
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
                    graph = build_driving_car(config.GRAPH_OSM_FILE, store=True, store_dir=config.GRAPH_DIR)
                    graph_cache["driving-car"] = graph
                case "walking-foot":
                    graph = build_walking_foot(config.GRAPH_OSM_FILE, store=True, store_dir=config.GRAPH_DIR)
                    graph_cache["walking-foot"] = graph
                case "public-transit":
                    if "walking-foot" in graph_cache:
                        graph = graph_cache["walking-foot"]
                    else:
                        graph = build_walking_foot(config.GRAPH_OSM_FILE, store=True, store_dir=config.GRAPH_DIR)
                        graph_cache["walking-foot"] = graph
                    graph = build_public_transit(graph, config.GRAPH_GTFS_DIR, config.GRAPH_GTFS_FILTER_POLYGON, store=True)
            profile_manager.add_profile(profile, graph, ["time"])
    return profile_manager

PROFILES = None

def init_profile_manager():
    """Initializes the profiles by loading or creating them.
    """
    global PROFILES
    PROFILES = _load_or_create_profiles()

def get_profile_manager() -> ProfileManager:
    """Returns the profile manager singleton.
    """
    global PROFILES
    if PROFILES is None:
        raise ValueError("This should not have happened.")
    return PROFILES
