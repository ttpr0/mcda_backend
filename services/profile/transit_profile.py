# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import numpy as np
import pyaccess

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
