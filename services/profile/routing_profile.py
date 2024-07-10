# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""Profile class for routing graphs.
"""

import numpy as np
import pyaccess

class RoutingProfile:
    """Profile class for routing graphs.
    """
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
