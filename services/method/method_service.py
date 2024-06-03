# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from __future__ import annotations

from fastapi import Depends
from typing import Any, Annotated, Protocol
import asyncio

import config
from .util import Infrastructure
from filters.user import get_current_user, User
from services.profile import ProfileManager, get_profile_manager
from .access_methods import AccessMethodService
from .oas_methods import OASMethodService

class IMethodService(Protocol):
    async def calcMultiCriteria(self, population_locations: list[tuple[float, float]], population_weights: list[int], infrastructures: dict[str, Infrastructure], travel_mode: str = "driving-car") -> tuple[dict[str, list[float]], dict[str, list[int]]]:
        ...

    async def calcFCA(self, population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], facility_weights: list[float], decay: dict, travel_mode: str = "driving-car") -> list[float]:
        ...

    async def calcSetCoverage(self, population_locations: list[tuple[float, float]], population_weights: list[int], facility_locations: list[tuple[float, float]], max_range: int, percent_coverage: float, travel_mode: str = "driving-car") -> list[bool]:
        ...

def get_method_service(
        profiles: Annotated[ProfileManager, Depends(get_profile_manager)],
        user: Annotated[User, Depends(get_current_user)]
    ) -> IMethodService:
    if user.get_group() in ["admin", "user"]:
        return AccessMethodService(profiles)
    elif user.get_group() in ["dummy"]:
        return OASMethodService(config.ACCESSIBILITYSERVICE_URL)
    else:
        raise ValueError(f"Invalid user group {user.get_group()}.")
