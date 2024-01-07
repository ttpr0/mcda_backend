# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from models.travel_modes import get_available_travelmodes, get_available_decays, get_default_timezones
from models.population import get_available_population
from models.facilities import get_available_facilities
from models.physicians import get_available_physicians
from models.planning_areas import get_available_supply_levels, get_available_planning_areas

router = APIRouter()

@router.get("/facilities")
async def get_facilities():
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
    return get_available_facilities()

@router.get("/population")
async def get_population():
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
    return get_available_population()

@router.get("/travel_modes")
async def get_travel_modes():
    """Returns all available travel modes as dictionary:
    ```json
    {
        "travel-mode": {"text": "i18n-key", "valid": True}
    }
    ```
    """
    return get_available_travelmodes()

@router.get("/distance_decays")
async def get_distance_decays():
    """Returns all available distance-decays
    ```json
    {
        "decay-name": {
            "text": "i18n-key"
        },
        ...
    }
    ```
    """
    return get_available_decays()

@router.post("/time_zones")
async def get_time_zones(req: Request):
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
    return get_default_timezones(data["facilities"])

@router.get("/supply_levels")
async def get_supply_levels():
    """Returns all available supply-levels
    ```json
    {
        "supply-level-name": {"text": "i18n-key", "valid": true},
        "supply-level-name": {"text": "i18n-key", "valid": false},
        ...
    }
    ```
    """
    return get_available_supply_levels()

@router.get("/planning_areas")
async def get_planning_areas():
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
    return get_available_planning_areas()

@router.get("/physicians")
async def get_physicians():
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
    return get_available_physicians()
