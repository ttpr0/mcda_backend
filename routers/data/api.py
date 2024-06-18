# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from shapely import Polygon
from typing import Annotated, cast
import asyncio
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from models.population import get_population_geometry
from models.facilities import get_facility
from models.planning_areas import get_planning_area
from helpers.util import get_extent, get_query_from_extent, get_buffered_query
from filters.user import get_current_user, User
from services.session import get_state, SessionStorage, Session

ROUTER = APIRouter()

class PopulationGeometryRequest(BaseModel):
    # query extent
    envelop: tuple[float, float, float, float] | None
    planning_area: str | None
    # population parameters
    population_type: str

@ROUTER.post("/grid")
async def population_geometry_api(
        req: PopulationGeometryRequest,
        state: Annotated[SessionStorage, Depends(get_state)],
        user: Annotated[User, Depends(get_current_user)]
    ):
    if req.planning_area is not None:
        query = get_planning_area(req.planning_area)
        if query is None:
            return {"error": "invalid request"}
    elif req.envelop is not None:
        query = get_query_from_extent(req.envelop)
    else:
        return {"error": "invalid request"}
    grid_indices, utm_points = get_population_geometry(query, req.population_type)

    features: list = []
    indices: list[int] = []
    minx, miny, maxx, maxy = get_extent(utm_points)
    for p, i in zip(utm_points, grid_indices):
        features.append([[p[0]-50, p[1]-50], [p[0]+50, p[1]-50], [p[0]+50, p[1]+50], [p[0]-50, p[1]+50]])
        indices.append(i)

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    return {"features": features, "indices": indices, "crs": crs, "extend": extend, "size": size}
