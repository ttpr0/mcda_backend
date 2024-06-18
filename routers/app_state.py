# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from typing import Annotated

from fastapi import APIRouter, Request, HTTPException, Depends

from functions.travel_modes import get_default_timezones
from functions.population import get_available_population
from functions.facilities import get_available_facilities
from functions.physicians import get_available_physicians
from functions.planning_areas import get_available_supply_levels, get_available_planning_areas
from filters.user import get_current_user, User
from services.database import AsyncSession, get_db_session

router = APIRouter()

@router.get("/facilities")
async def get_facilities(
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db_session)],
    ):
    """Returns all available facilities:
    ```json
    {
        "group-name": {
            "text": "i18n-key",
            "items": {
                "facility-name": {"text": "i18n-key"},
                "sub-group-name": {
                    "text": "i18n-key",
                    "items": {
                        "facility-name": {"text": "i18n-key"},
                        ...
                    }
                }
                ...
            }
        }
        ...
    }
    ```
    """
    return await get_available_facilities(db)

@router.get("/population")
async def get_population(
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db_session)],
    ):
    """Returns all available population parameters:
    ```json
    {
        "standard": {
            "text": "i18n-key",
            "items": {
                "age-group-name": (age-min, age-max),
                "age-group-name": (age-min, age-max),
                ...
            }
        },
        "population-name": {
            ...
        },
        ...
    }
    ```
    """
    return await get_available_population(db)

@router.post("/time_zones")
async def get_time_zones(
        req: Request,
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db_session)],
    ):
    """Returns time-zones for all requested facilities

    Time-zones are four integers defining the travel-time thresholds for very-good, good, sufficient and above deficient supply.

    Request:
    ```json
    {
        "facilities": [
            "facility-1", "facility-2", ...
        ]
    }
    ```

    Response:
    ```json
    {
        "facility-1": (very-good, good, sufficient, above deficient),
        "facility-2": (very-good, good, sufficient, above deficient),
        ...
    }
    ```
    """
    data = await req.json()
    if "facilities" not in data:
        raise HTTPException(status_code=404, detail="key 'facilities' not provided")
    return await get_default_timezones(db, data["facilities"]) # type: ignore

@router.get("/supply_levels")
async def get_supply_levels(
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db_session)],
    ):
    """Returns all available supply-levels
    ```json
    {
        "supply-level-name": {"text": "i18n-key", "valid": true},
        "supply-level-name": {"text": "i18n-key", "valid": false},
        ...
    }
    ```
    """
    return await get_available_supply_levels(db)

@router.get("/planning_areas")
async def get_planning_areas(
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db_session)],
    ):
    """Returns all available planning-areas per supply-level
    ```json
    {
        "supply-level-name": {
            "planning-area-name": {"text": "i18n-key"},
            ...
        },
        ...
    }
    ```
    """
    return await get_available_planning_areas(db)

@router.get("/physicians")
async def get_physicians(
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db_session)],
    ):
    """Returns all available physicians per supply-level
    ```json
    {
        "supply-level-name": {
            "physican-name": {"text": "i18n-key"},
            ...
        },
        ...
    }
    ```
    """
    return await get_available_physicians(db)

@router.get("/ui_settings")
async def get_ui_settings(user: Annotated[User, Depends(get_current_user)]):
    return {
        "storeParameters": False,
        "loadParameters": False
    }

@router.get("/analysis_settings")
async def get_analysis_settings(user: Annotated[User, Depends(get_current_user)]):
    return {
        "statistics": {
            "a": True,
            "b": True,
            "c": True
        },
        "hotspot": True,
        "scenario": True
    }

@router.get("/range_limits")
async def get_range_limits(user: Annotated[User, Depends(get_current_user)]):
    return {
        "min": 0,
        "max": 70
    }
