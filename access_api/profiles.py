from enum import Enum
from typing import Protocol
import numpy as np
import pyaccess

import config

class Profile(Enum):
    DRIVING = 1
    TRANSIT = 2
    WALKING = 3
    CYCLING = 4

class IRoutingProfile(Protocol):
    def calc_reachability(self, dem_points: list[tuple[float, float]], sup_points: list[tuple[float, float]], decay: pyaccess._pyaccess_ext.IDistanceDecay) -> np.ndarray:
        ...

class RoutingProfile:
    _graph: pyaccess.Graph

    def __init__(self, graph: pyaccess.Graph):
        self._graph = graph

    def calc_reachability(self, dem_points: list[tuple[float, float]], sup_points: list[tuple[float, float]], decay: pyaccess._pyaccess_ext.IDistanceDecay) -> np.ndarray:
        return pyaccess.calc_reachability(self._graph, dem_points, sup_points, decay)

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

    def calc_reachability(self, dem_points: list[tuple[float, float]], sup_points: list[tuple[float, float]], decay: pyaccess._pyaccess_ext.IDistanceDecay) -> np.ndarray:
        return pyaccess.calc_reachability(self._graph, dem_points, sup_points, decay=decay, transit="transit", transit_weight=self._weekday, min_departure=self._min_departure, max_departure=self._max_departure)

class ProfileData:
    _type: Profile
    _graph: pyaccess.Graph

    def __init__(self, type: Profile, graph: pyaccess.Graph):
        self._type = type
        self._graph = graph

class ProfileManager:
    _profiles: dict[str, ProfileData]

    def __init__(self):
        self._graphs = {}
        self.profiles = {}

    def add_profile(self, name: str, type: Profile, graph: pyaccess.Graph):
        self._profiles[name] = ProfileData(type, graph)

    def has_profile(self, name: str) -> bool:
        return name in self._profiles

    def get_profile(self, profile: str, weekday: str = "wednesday", timespan: tuple[int , int]= (0, 100000)) -> IRoutingProfile | None:
        params = self._profiles[profile]
        graph = params._graph
        match params._type:
            case Profile.DRIVING, Profile.WALKING, Profile.CYCLING:
                return RoutingProfile(graph)
            case Profile.TRANSIT:
                return TransitProfile(graph, weekday, timespan[0], timespan[1])
            case _:
                return None

def load_or_create_profiles():
    profile_manager = ProfileManager()
    # load or create profiles
    for profile in config.ROUTING_PROFILES:
        if profile_manager.has_profile(profile):
            continue
        try:
            graph = pyaccess.load_graph(profile, config.GRAPH_DIR)
        except:
            match profile:
                case "driving-car":
                    profile_type = Profile.DRIVING
                    profile_decoder = "driving"
                case "walking-foot":
                    profile_type = Profile.WALKING
                    profile_decoder = "walking"
                case "cycling-bike":
                    profile_type = Profile.CYCLING
                    profile_decoder = "cycling"
                case "public-transit":
                    profile_type = Profile.TRANSIT
                    profile_decoder = "walking"
            graph = pyaccess.parse_osm(config.GRAPH_OSM_FILE, profile_decoder)
            graph.optimize_base()
            graph.add_default_weighting()
            if profile == "public-transit":
                stops, conns, schedules = pyaccess.parse_gtfs(config.GRAPH_GTFS_DIR, config.GRAPH_GTFS_FILTER_POLYGON)
                graph.add_public_transit("transit", stops, conns)
                for day, schedule in schedules.items():
                    weight = pyaccess.new_transit_weighting(graph, "transit")
                    for i, conn in enumerate(schedule):
                        weight.set_connection_schedule(i, conn)
                    graph.add_transit_weighting(day, weight, "transit")
            graph.store(profile, config.GRAPH_DIR)
        profile_manager.add_profile(profile, profile_type, graph)
    return profile_manager
