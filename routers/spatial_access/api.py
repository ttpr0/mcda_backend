# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Annotated

from functions.population import get_population_values
from functions.physicians import get_physicians
from functions.planning_areas import get_planning_area
from functions.travel_modes import get_distance_decay, is_valid_travel_mode, get_default_travel_mode
from filters.user import get_current_user, User
from services.method import get_method_service, IMethodService, Infrastructure
from services.database import AsyncSession, get_db_session

ROUTER = APIRouter()

class SpatialAccessRequest(BaseModel):
    # query extent
    supply_level: str
    planning_area: str
    # facility parameters
    facility_type: str
    facility_capacity: str
    # population parameters
    population_type: str
    population_grid_indices: list[int]
    population_indizes: list[str] | None
    #routing parameters
    travel_mode: str
    decay_type: str

@ROUTER.post("/grid")
async def spatial_access_api(
        req: SpatialAccessRequest,
        method_service: Annotated[IMethodService, Depends(get_method_service)],
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db_session)],
    ):
    query = await get_planning_area(db, req.planning_area)
    if query is None:
        return {"error": "invalid request"}
    buffer_query = query.buffer(0.2)

    if req.population_indizes is None or req.population_type is None:
        population_locations, population_weights = await get_population_values(db, query=buffer_query, indices=req.population_grid_indices)
    else:
        population_locations, population_weights = await get_population_values(db, query=buffer_query, indices=req.population_grid_indices, typ=req.population_type, age_groups=req.population_indizes)
    facility_points, facility_weights = await get_physicians(db, buffer_query, req.facility_type, req.facility_capacity)
    distance_decay = get_distance_decay(req.travel_mode, req.decay_type, req.supply_level, req.facility_type)
    travel_mode = req.travel_mode
    if not is_valid_travel_mode(travel_mode):
        travel_mode = get_default_travel_mode()

    accessibilities = await method_service.calcFCA(population_locations, population_weights, facility_points, facility_weights, distance_decay, travel_mode)

    features: list = []
    min_val = 1000000000
    max_val = -1000000000
    for i in range(len(req.population_grid_indices)):
        access: float = float(accessibilities[i])
        if not access == -9999: 
            if access < min_val:
                min_val = access
            if access > max_val:
                max_val = access
        features.append({
            "accessibility": access,
        })

    return {"features": features, "min": min_val, "max": max_val}
