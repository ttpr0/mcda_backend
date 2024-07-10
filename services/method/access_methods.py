# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""IMethodService implementations using pyaccess.
"""

from .util import get_distance_decay, Infrastructure
from services.profile import ProfileManager

class AccessMethodService:
    _profiles: ProfileManager

    def __init__(self, profiles: ProfileManager):
        self._profiles = profiles

    async def calcFCA(self, population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], decay: dict, travel_mode: str = "driving-car") -> list[float]:
        profile = self._profiles.get_profile(travel_mode)
        if profile is None:
            raise ValueError(f"Invalid profile {travel_mode}.")
        distance_decay = get_distance_decay(decay)
        if distance_decay is None:
            raise ValueError(f"Invalid decay parameters {decay}.")
        arr = profile.calc_2sfca(population_locations, population_weights, facility_locations, [int(i) for i in facility_weights], distance_decay)
        return arr.tolist()

    async def calcMultiCriteria(self, population_locations: list[tuple[float, float]], population_weights: list[int], infrastructures: dict[str, Infrastructure], travel_mode: str = "driving-car") -> tuple[dict[str, list[float]], dict[str, list[int]]]:
        profile = self._profiles.get_profile(travel_mode)
        if profile is None:
            raise ValueError(f"Invalid profile {travel_mode}.")
        access = {}
        access["multiCriteria"] = [0] * len(population_locations)
        counts = {}
        # weight_sum = sum([i.weight for i in infrastructures.values()])
        for name, infra in infrastructures.items():
            decay = get_distance_decay(infra.decay)
            if decay is None:
                raise ValueError(f"Invalid decay parameters {infra.decay}.")
            reach, count = profile.calc_reachability(population_locations, infra.locations, decay)
            counts[name] = count
            weight = infrastructures[name].weight
            multi = access["multiCriteria"]
            for j in range(len(population_locations)):
                if reach[j] <= 0:
                    reach[j] = -9999
                    continue
                multi[j] += weight * reach[j]
            access[name] = reach.tolist()
        multi = access["multiCriteria"]
        for j in range(len(population_locations)):
            if multi[j] <= 0:
                multi[j] = -9999
        return access, counts

    async def calcSetCoverage(self, population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], max_range: int, percent_coverage: float, travel_mode: str = "driving-car") -> list[bool]:
        profile = self._profiles.get_profile(travel_mode)
        if profile is None:
            raise ValueError(f"Invalid profile {travel_mode}.")
        arr = profile.calc_set_coverage(population_locations, population_weights, facility_locations, max_range, percent_coverage)
        return arr.tolist()
