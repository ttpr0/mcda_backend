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
from helpers.util import get_extent
from helpers.depends import get_current_user, User
from access_api.multi_criteria import Infrastructure, calcMultiCriteria
from helpers.dummy_decay import get_dummy_decay

STATE = {}


router = APIRouter()

class InfrastructureParams(BaseModel):
    infrastructure_weight: float
    distance_decay: dict
    cutoff_points: list[int]
    facility_type: str

class MultiCriteriaRequest(BaseModel):
    # infrastructure parameters
    infrastructures: dict[str, InfrastructureParams]
    # query extent
    envelop: tuple[float, float, float, float]
    # population parameters
    population_type: str
    population_indizes: list[str]|None
    # travel parameters
    travel_mode: str


@router.post("/grid")
async def decision_support_api(req: MultiCriteriaRequest, user: Annotated[User, Depends(get_current_user)]):
    ll = (req.envelop[0], req.envelop[1])
    ur = (req.envelop[2], req.envelop[3])
    query = Polygon(((ll[0], ll[1]), (ll[0], ur[1]), (ur[0], ur[1]), (ur[0], ll[1])))
    buffer_query = query.buffer(0.2)
    if req.population_indizes is None or req.population_type is None:
        population_locations, utm_points, population_weights = get_population(query)
    else:
        population_locations, utm_points, population_weights = get_population(query, req.population_type, req.population_indizes)

    infrastructures = {}
    for name, param in req.infrastructures.items():
        facility_points, facility_weights = get_facility(param.facility_type, buffer_query)
        infrastructures[name] = Infrastructure(param.infrastructure_weight, param.distance_decay, param.cutoff_points, facility_points, facility_weights)

    task = asyncio.create_task(calcMultiCriteria(population_locations, population_weights, infrastructures, req.travel_mode))

    features: list = []
    minx, miny, maxx, maxy = get_extent(utm_points)
    for p, w in zip(utm_points, population_weights):
        features.append({
            "coordinates": [p[0], p[1]],
            "properties": {
                "population": w
            }
        })

    accessibilities = await task
    accessibilities["population"] = cast(list[float], population_weights)

    global STATE
    STATE[user.get_name()] = {
        "accessibilities": accessibilities,
        "infrastructures": infrastructures,
    }

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

@router.post("/analysis/stat_1")
async def stat_1_api(user: Annotated[User, Depends(get_current_user)]):
    """Computes the amount of different facility-types serving each population-cell
    """
    access = STATE[user.get_name()]["accessibilities"]
    population = access["population"]
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

class AnalysisRequest(BaseModel):
    facility: str

@router.post("/analysis/stat_2")
async def stat_2_api(req: AnalysisRequest, user: Annotated[User, Depends(get_current_user)]):
    """Computes the quality of supply serving each population cell for each infrastructure
    """
    access = STATE[user.get_name()]["accessibilities"]
    values: list[float] = access[req.facility]
    population: list[int] = access["population"]
    infras = STATE[user.get_name()]["infrastructures"]
    infra: Infrastructure = infras[req.facility]
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
    unique, counts = np.unique(quality, return_counts=True)
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

@router.post("/analysis/stat_3")
async def stat_3_api(req: AnalysisRequest, user: Annotated[User, Depends(get_current_user)]):
    access = STATE[user.get_name()]["accessibilities"]
    values: list[float] = access[req.facility]
    numbers = np.random.randint(0, 10, (len(values),))
    unique, counts = np.unique(numbers, return_counts=True)
    # create plotly plot
    fig = go.Figure()
    fig.add_bar(x=[str(i) for i in list(reversed(unique.tolist()))], y=list(reversed(counts.tolist())))
    fig.update_layout(
        xaxis={"title": 'Anzahl der Versorgungspunkte'},
        yaxis={"title": 'Bevölkerungsanzahl'},
        margin=dict(l=10, r=10, t=10, b=10),
        minreducedwidth=250,
        minreducedheight=250,
        autosize= True,
    )
    return Response(content=fig.to_json(), media_type="application/json")

@router.post("/analysis/hotspot")
async def hotspot_api(user: Annotated[User, Depends(get_current_user)]):
    access = STATE[user.get_name()]["accessibilities"]
    population = access["population"]
    multi = access["multiCriteria"]
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
