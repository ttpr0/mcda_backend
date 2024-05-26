# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from __future__ import annotations

from access_api.multi_criteria import Infrastructure


class DecisionSupportSession:
    _accessibilities: dict[str, list[float]] | None
    _counts: dict[str, list[int]] | None
    _population: tuple[list[tuple[float, float]], list[int]] | None
    _infrastructures: dict[str, Infrastructure] | None

    def __init__(self):
        self._accessibilities = None
        self._population = None
        self._infrastructures = None

    def has_accessibility(self) -> bool:
        return self._accessibilities is not None
    
    def has_counts(self) -> bool:
        return self._counts is not None
    
    def has_population(self) -> bool:
        return self._population is not None
    
    def has_infrastructures(self) -> bool:
        return self._infrastructures is not None

    def get_accessibilities(self) -> dict[str, list[float]]:
        if self._accessibilities is None:
            raise Exception("Accessibilities not set")
        return self._accessibilities
    
    def get_counts(self) -> dict[str, list[int]]:
        if self._counts is None:
            raise Exception("Counts not set")
        return self._counts

    def get_population(self) -> tuple[list[tuple[float, float]], list[int]]:
        if self._population is None:
            raise Exception("Population not set")
        return self._population

    def get_infrastructures(self) -> dict[str, Infrastructure]:
        if self._infrastructures is None:
            raise Exception("Infrastructures not set")
        return self._infrastructures

    def set_accessibilities(self, accessibilities: dict[str, list[float]]):
        self._accessibilities = accessibilities

    def set_counts(self, counts: dict[str, list[int]]):
        self._counts = counts

    def set_population(self, population: tuple[list[tuple[float, float]], list[int]]):
        self._population = population

    def set_infrastructures(self, infrastructures: dict[str, Infrastructure]):
        self._infrastructures = infrastructures

