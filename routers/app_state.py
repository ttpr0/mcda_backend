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
    return get_available_facilities()

@router.get("/population")
async def get_population():
    return get_available_population()

@router.get("/travel_modes")
async def get_travel_modes():
    return get_available_travelmodes()

@router.get("/distance_decays")
async def get_distance_decays():
    return get_available_decays()

@router.post("/time_zones")
async def get_time_zones(req: Request):
    data = await req.json()
    if "facilities" not in data:
        raise HTTPException(status_code=404, detail="key 'facilities' not provided")
    return get_default_timezones(data["facilities"])

@router.get("/supply_levels")
async def get_supply_levels():
    return get_available_supply_levels()

@router.get("/planning_areas")
async def get_planning_areas():
    return get_available_planning_areas()

@router.get("/physicans")
async def get_physicians():
    return get_available_physicians()
