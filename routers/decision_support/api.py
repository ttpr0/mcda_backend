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

from models.population import get_population
from models.facilities import get_facility
from helpers.util import get_extent, get_query_from_extent, get_buffered_query
from filters.user import get_current_user, User
from helpers.dummy_decay import get_dummy_decay
from services.method import get_method_service, IMethodService, Infrastructure
from services.session import get_state, SessionStorage, Session

ROUTER = APIRouter()

@ROUTER.post("/create_session")
async def create_session(
        state: Annotated[SessionStorage, Depends(get_state)],
        user: Annotated[User, Depends(get_current_user)]
    ):
    session_id = state.new_session(user.get_name())
    return {
        "session_id": session_id
    }

class InfrastructureParams(BaseModel):
    infrastructure_weight: float
    distance_decay: dict
    cutoff_points: list[int]
    facility_type: str

class MultiCriteriaRequest(BaseModel):
    session_id: str
    # infrastructure parameters
    infrastructures: dict[str, InfrastructureParams]
    # query extent
    envelop: tuple[float, float, float, float]
    # population parameters
    population_type: str
    population_indizes: list[str]|None
    # travel parameters
    travel_mode: str

@ROUTER.post("/grid")
async def decision_support_api(
        req: MultiCriteriaRequest,
        method_service: Annotated[IMethodService, Depends(get_method_service)],
        state: Annotated[SessionStorage, Depends(get_state)],
        user: Annotated[User, Depends(get_current_user)]
    ):
    query = get_query_from_extent(req.envelop)
    if req.population_indizes is None or req.population_type is None:
        population_locations, utm_points, population_weights = get_population(query)
    else:
        population_locations, utm_points, population_weights = get_population(query, req.population_type, req.population_indizes)

    infrastructures = {}
    for name, param in req.infrastructures.items():
        buffer_query = get_buffered_query(query, req.travel_mode, param.distance_decay)
        facility_points, facility_weights = get_facility(param.facility_type, buffer_query)
        infrastructures[name] = Infrastructure(param.infrastructure_weight, param.distance_decay, param.cutoff_points, facility_points, facility_weights)

    task = asyncio.create_task(method_service.calcMultiCriteria(population_locations, population_weights, infrastructures, req.travel_mode))

    features: list = []
    minx, miny, maxx, maxy = get_extent(utm_points)
    for p, w in zip(utm_points, population_weights):
        features.append({
            "coordinates": [p[0], p[1]],
            "properties": {
                "population": w
            }
        })

    accessibilities, counts = await task

    # update session
    session = state.get_session(user.get_name(), req.session_id)
    session["accessibilities"] = accessibilities
    session["counts"] = counts
    session["infrastructures"] = infrastructures
    session["population"]  = (population_locations, population_weights)
    session.commit()

    for name, array in accessibilities.items():
        for i, _ in enumerate(utm_points):
            feature = features[i]
            access: float = float(array[i])
            feature["properties"][name] = access

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    return {"features": features, "crs": crs, "extend": extend, "size": size}

class Analysis1Request(BaseModel):
    session_id: str

@ROUTER.post("/analysis/stat_1")
async def stat_1_api(
        req: Analysis1Request,
        state: Annotated[SessionStorage, Depends(get_state)],
        user: Annotated[User, Depends(get_current_user)]
    ):
    """Computes the amount of different facility-types serving each population-cell
    """
    # get session state
    session = state.get_session(user.get_name(), req.session_id)
    access: dict[str, list[float]] = session["accessibilities"]
    population: list[int]
    _, population = session["population"]
    # compute statistics
    amount = np.zeros((len(population,)), dtype=np.int32)
    facility_count = 0
    for key in access.keys():
        if key in ["population", "multiCriteria"]:
            continue
        facility_count += 1
        values = access[key]
        for i in range(len(population)):
            if values[i] == -9999:
                continue
            amount[i] += 1
    df = pd.DataFrame({"amount": amount, "population": population})
    group = df.groupby('amount')
    agg = group.aggregate({'population': 'sum'})
    labels = []
    data = []
    for i in range(facility_count, -1, -1):
        labels.append(str(i))
        if i in agg.index:
            data.append(int(agg.loc[i, "population"])) # type: ignore
        else:
            data.append(0)
    # create plotly plot
    fig = go.Figure()
    fig.add_bar(x=labels, y=data)
    fig.update_layout(
        xaxis={"title": 'Anzahl der Infrastrukturarten'},
        yaxis={"title": 'Bevölkerungsanzahl'},
        margin=dict(l=10, r=10, t=10, b=10),
        minreducedwidth=250,
        minreducedheight=250,
        autosize= True,
    )
    return Response(content=fig.to_json(), media_type="application/json")

class Analysis2Request(BaseModel):
    session_id: str
    facility: str

@ROUTER.post("/analysis/stat_2")
async def stat_2_api(
        req: Analysis2Request,
        state: Annotated[SessionStorage, Depends(get_state)],
        user: Annotated[User, Depends(get_current_user)]
    ):
    """Computes the quality of supply serving each population cell for each infrastructure
    """
    # get session state
    session = state.get_session(user.get_name(), req.session_id)
    access: dict[str, list[float]] = session["accessibilities"]
    values: list[float] = access[req.facility]
    population: list[int]
    _, population = session["population"]
    infras: dict[str, Infrastructure] = session["infrastructures"]
    infra = infras[req.facility]
    # compute statistics
    decay = get_dummy_decay(infra.decay)
    cutoff_points = [decay.get_distance_weight(int(i)) - 0.0001 for i in infra.cutoffs]
    quality = np.zeros((len(values,)), dtype=np.int32)
    for i in range(len(values)):
        quality[i] = len(infra.cutoffs)
        if values[i] == -9999:
            continue
        for j, p in enumerate(cutoff_points):
            if values[i] >= p:
                quality[i] = j
                break
    df = pd.DataFrame({"quality": quality, "population": population})
    group = df.groupby('quality')
    agg = group.aggregate({'population': 'sum'})
    data = []
    for i in range(0, 5):
        if i in agg.index:
            data.append(int(agg.loc[i, "population"])) # type: ignore
        else:
            data.append(0)
    # create plotly plot
    fig = go.Figure()
    fig.add_bar(x=["sehr gut", "gut", "ausreichend", "mangelhaft", "ungenügend"], y=data)
    fig.update_layout(
        xaxis={"title": 'Qualität der Versorgung'},
        yaxis={"title": 'Bevölkerungsanzahl'},
        margin=dict(l=10, r=10, t=10, b=10),
        minreducedwidth=250,
        minreducedheight=250,
        autosize= True,
    )
    return Response(content=fig.to_json(), media_type="application/json")

class Analysis3Request(BaseModel):
    session_id: str
    facility: str

@ROUTER.post("/analysis/stat_3")
async def stat_3_api(
        req: Analysis3Request,
        state: Annotated[SessionStorage, Depends(get_state)],
        user: Annotated[User, Depends(get_current_user)]
    ):
    # get session state
    session = state.get_session(user.get_name(), req.session_id)
    counts: dict[str, list[int]] = session["counts"]
    population: list[int]
    _, population = session["population"]
    values: list[int] = counts[req.facility]
    # compute statistics
    df = pd.DataFrame({"counts": values, "population": population})
    group = df.groupby('counts')
    agg = group.aggregate({'population': 'sum'})
    x = []
    y = []
    for i, row in agg.iterrows():
        x.append(int(i)) # type: ignore
        y.append(int(row['population']))
    # create plotly plot
    fig = go.Figure()
    fig.add_bar(x=[str(i) for i in x], y=y)
    fig.update_layout(
        xaxis={"title": 'Anzahl der Versorgungspunkte'},
        yaxis={"title": 'Bevölkerungsanzahl'},
        margin=dict(l=10, r=10, t=10, b=10),
        minreducedwidth=250,
        minreducedheight=250,
        autosize= True,
    )
    return Response(content=fig.to_json(), media_type="application/json")

class HotspotRequest(BaseModel):
    session_id: str

@ROUTER.post("/analysis/hotspot")
async def hotspot_api(
        req: HotspotRequest,
        state: Annotated[SessionStorage, Depends(get_state)],
        user: Annotated[User, Depends(get_current_user)]
    ):
    # get session state
    session = state.get_session(user.get_name(), req.session_id)
    access: dict[str, list[float]] = session["accessibilities"]
    multi: list[float] = access["multiCriteria"]
    population: list[int]
    _, population = session["population"]
    # compute statistics
    xs = []
    ys = []
    for i in range(len(population)):
        x = population[i]
        y = multi[i]
        if y == -9999:
            continue
        xs.append(x)
        ys.append(y)
    # create plotly plot
    fig = go.Figure()
    fig.add_scatter(x=xs, y=ys, mode='markers')
    fig.update_layout(
        xaxis={"title": 'Bevölkerung der Bevölkerungszelle'},
        yaxis={"title": 'Versorgung der Bevölkerungszelle'},
        margin=dict(l=10, r=10, t=10, b=10),
        minreducedwidth=250,
        minreducedheight=250,
        autosize= True,
    )
    return Response(content=fig.to_json(), media_type="application/json")

class FeaturesRequest(BaseModel):
    # infrastructure parameters
    infrastructures: dict[str, InfrastructureParams]
    # query extent
    envelop: tuple[float, float, float, float]
    # travel mode
    travel_mode: str

@ROUTER.post("/features")
async def scenario_features_api(
        req: FeaturesRequest,
        user: Annotated[User, Depends(get_current_user)]
    ):
    query = get_query_from_extent(req.envelop)

    data = {}
    for name, param in req.infrastructures.items():
        buffer_query = get_buffered_query(query, req.travel_mode, param.distance_decay)
        facility_points, facility_weights = get_facility(param.facility_type, buffer_query)
        features = []
        for p, w in zip(facility_points, facility_weights):
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",               
                    "coordinates": [p[0], p[1]],
                },
                "properties": {
                    "weight": w
                }
            })
        data[name] = {
            "type": "FeatureCollection",
            "features": features
        }

    return data

class InfrastructureParams2(BaseModel):
    infrastructure_weight: float
    distance_decay: dict
    cutoff_points: list[int]
    facility_locations: list[tuple[float, float]]

class ScenarioRequest(BaseModel):
    # infrastructure parameters
    infrastructures: dict[str, InfrastructureParams2]
    # query extent
    envelop: tuple[float, float, float, float]
    # population parameters
    population_type: str
    population_indizes: list[str]|None
    # travel parameters
    travel_mode: str

@ROUTER.post("/scenario")
async def scenario_api(
        req: ScenarioRequest,
        method_service: Annotated[IMethodService, Depends(get_method_service)],
        user: Annotated[User, Depends(get_current_user)]
    ):
    query = get_query_from_extent(req.envelop)
    if req.population_indizes is None or req.population_type is None:
        population_locations, utm_points, population_weights = get_population(query)
    else:
        population_locations, utm_points, population_weights = get_population(query, req.population_type, req.population_indizes)

    infrastructures = {}
    for name, param in req.infrastructures.items():
        buffer_query = get_buffered_query(query, req.travel_mode, param.distance_decay)
        facility_points = param.facility_locations
        infrastructures[name] = Infrastructure(param.infrastructure_weight, param.distance_decay, param.cutoff_points, facility_points, [])

    task = asyncio.create_task(method_service.calcMultiCriteria(population_locations, population_weights, infrastructures, req.travel_mode))

    features: list = []
    minx, miny, maxx, maxy = get_extent(utm_points)
    for p, w in zip(utm_points, population_weights):
        features.append({
            "coordinates": [p[0], p[1]],
            "properties": {
                "population": w
            }
        })

    accessibilities, _ = await task

    for name, array in accessibilities.items():
        for i, _ in enumerate(utm_points):
            feature = features[i]
            access: float = float(array[i])
            feature["properties"][name] = access

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    return {"features": features, "crs": crs, "extend": extend, "size": size}

class InfrastructureParams3(BaseModel):
    max_range: int
    coverage_target: float
    facility_locations: list[tuple[float, float]]

class OptimizationRequest(BaseModel):
    # infrastructure parameters
    infrastructures: dict[str, InfrastructureParams3]
    # query extent
    envelop: tuple[float, float, float, float]
    # population parameters
    population_type: str
    population_indizes: list[str]|None
    # travel parameters
    travel_mode: str

@ROUTER.post("/optimization")
async def scenario_optimization_api(
        req: OptimizationRequest,
        method_service: Annotated[IMethodService, Depends(get_method_service)],
        user: Annotated[User, Depends(get_current_user)]
    ):
    query = get_query_from_extent(req.envelop)
    if req.population_indizes is None or req.population_type is None:
        population_locations, _, population_weights = get_population(query)
    else:
        population_locations, _, population_weights = get_population(query, req.population_type, req.population_indizes)

    result = {}
    for name, param in req.infrastructures.items():
        r = await method_service.calcSetCoverage(population_locations, population_weights, param.facility_locations, param.max_range, param.coverage_target, req.travel_mode)
        result[name] = r

    return result
