# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter
from pydantic import BaseModel
from shapely import Point, Polygon, contains_xy
from typing import Any
import requests
import json
import asyncio
import time
import os
import numpy as np
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

import config
from helpers.population import get_population
from helpers.facilities import get_facility
from helpers.util import get_extent
from access.fca import calcFCA

# from helpers.geoserver_api import add_featurestore, open_conncection
# from helpers.postgis_api import add_results

from models import engine, PlanningArea, PhysiciansLocationBased, PhysiciansCountBased, PhysiciansList

def getPlanningArea(supply_level: str, planning_area: str) -> Polygon|None:
    with Session(engine) as session:
        rows = session.query(PlanningArea).where(PlanningArea.name == planning_area)
        for row in rows:
            return to_shape(row.geom)
        return None

# planning_areas: dict|None = None

# def getPlanningArea(supply_level: str, planning_area: str) -> Polygon|None:
#     global planning_areas
#     # load physicians data
#     if planning_areas is None:
#         planning_areas = {}
#         for file in os.listdir(config.PLANNING_AREAS_DIR):
#             if not os.path.isfile(os.path.join(config.PLANNING_AREAS_DIR, file)):
#                 continue
#             with open(config.PLANNING_AREAS_DIR + "/" + file, "r") as file:
#                 data = json.loads(file.read())
#                 for feature in data["features"]:
#                     name = feature["attributes"]["HPB"]
#                     rings = feature["geometry"]["rings"]
#                     polygon = Polygon(rings[0], rings[1:])
#                     planning_areas[name] = polygon
#     if planning_area not in planning_areas:
#         return None
#     query = planning_areas[planning_area]
#     return query


def getFacilities(query: Polygon, supply_level: str, facility_type: str, facility_cap: str) -> tuple[list[tuple[float, float]], list[float]]:    
    locations = []
    weights = []
    
    with Session(engine) as session:
        rows = session.query(PhysiciansList).where(PhysiciansList.name == facility_type)
        detail_id = None
        for row in rows:
            detail_id = row.detail_id
        if detail_id is None:
            return (locations, weights)

        if facility_cap == 'facility':
            rows = session.query(PhysiciansLocationBased).where(
                (PhysiciansLocationBased.detail_id == detail_id) & PhysiciansLocationBased.point.ST_Within(query.wkt)
            )
            for row in rows:
                point = to_shape(row.point)
                locations.append((point.x, point.y))
                weights.append(row.count)
        elif facility_cap == 'physicianNumber':
            rows = session.query(PhysiciansCountBased).where(
                (PhysiciansCountBased.detail_id == detail_id) & PhysiciansCountBased.point.ST_Within(query.wkt)
            )
            for row in rows:
                point = to_shape(row.point)
                locations.append((point.x, point.y))
                weights.append(row.vbe_sum)
        elif facility_cap == 'employmentVolume':
            rows = session.query(PhysiciansCountBased).where(
                (PhysiciansCountBased.detail_id == detail_id) & PhysiciansCountBased.point.ST_Within(query.wkt)
            )
            for row in rows:
                point = to_shape(row.point)
                locations.append((point.x, point.y))
                weights.append(row.pys_count)
    
    return (locations, weights)

# physicians_location_based: list|None = None
# physicians_count_based: list|None = None

# def getFacilities(query: Polygon, supply_level: str, facility_type: str, facility_cap: str) -> tuple[list[tuple[float, float]], list[float]]:
#     global physicians_location_based, physicians_count_based
#     # load physicians data
#     if physicians_location_based is None:
#         physicians_location_based = []
#         with open(config.SPATIAL_ACCESS_DIR + "/outpatient_physicians_location_based.geojson", "r") as file:
#             data = json.loads(file.read())
#             for feature in data["features"]:
#                 props = feature["properties"]
#                 point = Point(feature["geometry"]["coordinates"])
#                 physicians_location_based.append({
#                     "point": point,
#                     "TYP_ID": int(props["TYP_ID"]),
#                     "DETAIL_ID": int(props["DETAIL_ID_1"]),
#                     "count": 1,
#                 })
#     if physicians_count_based is None:
#         physicians_count_based = []
#         with open(config.SPATIAL_ACCESS_DIR + "/outpatient_physician_location_specialist_count.geojson", "r") as file:
#             data = json.loads(file.read())
#             for feature in data["features"]:
#                 props = feature["properties"]
#                 point = Point(feature["geometry"]["coordinates"])
#                 physicians_count_based.append({
#                     "point": point,
#                     "TYP_ID": int(props["TYP_ID"]),
#                     "DETAIL_ID": int(props["DETAIL_ID_1"]),
#                     "VBE_Sum": float(props["VBE_Sum"]),
#                     "Pys_Count": float(props["Pys_count"]),
#                 })
    
#     # map supply level
#     typ_id = 0
#     match supply_level:
#         case 'generalPhysician':
#             typ_id = 100
#         case 'generalSpecialist':
#             typ_id = 200
#         case 'specializedSpecialist':
#             typ_id = 300
    
#     # map physican type
#     detail_id = 0
#     match facility_type:
#         case "Hausärzte":
#             detail_id = 100
#         case "Augenärzte":
#             detail_id = 205
#         case "Chirurgen und Orthopäden":
#             detail_id = 212
#         case "Frauenärzte":
#             detail_id = 235
#         case "Hautärzte":
#             detail_id = 225
#         case "HNO-Ärzte":
#             detail_id = 220
#         case "Kinderärzte":
#             detail_id = 245
#         case "Nervenärzte":
#             detail_id = 230
#         case "Psychotherapeuten":
#             detail_id = 250
#         case "Urologen":
#             detail_id = 240
#         case "fachärztlich tätige Internisten":
#             detail_id = 302
#         case "Kinder- und Jugendpsychiater":
#             detail_id = 303
#         case "Radiologen":
#             detail_id = 304
#         case "Anästhesisten":
#             detail_id = 301

#     if (detail_id - typ_id) < 0:
#         return ([], [])

#     locations = []
#     weights = []
    
#     physicians_list = None
#     physician_prop = None
#     if facility_cap == 'facility':
#         physicians_list = physicians_location_based
#         physician_prop = "count"
#     elif facility_cap == 'physicianNumber':
#         physicians_list = physicians_count_based
#         physician_prop = "VBE_Sum"
#     elif facility_cap == 'employmentVolume':
#         physicians_list = physicians_count_based
#         physician_prop = "Pys_Count"
#     else:
#         return ([], [])

#     for physician in physicians_list:
#         point = physician["point"]
#         if detail_id == physician["DETAIL_ID"] and query.contains(point):
#             locations.append((point.x, point.y))
#             weights.append(physician[physician_prop])
    
#     return (locations, weights)

def getDistanceDecay(travel_mode: str, decay_type: str, supply_level: str, facility_type: str) -> tuple[list[float], list[float]]:
    if decay_type == 'linear':
        if supply_level == "generalPhysician":
            ranges = [120., 240., 360., 480., 600., 720., 840., 960., 1080., 1200.]
            factors = [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            return (ranges, factors)
        elif supply_level == "generalSpecialist" and facility_type != "Kinderärzte":
            ranges = [240., 480., 720., 960., 1200., 1440., 1680., 1920., 2160., 2400.]
            factors = [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            return (ranges, factors)
        elif supply_level == "generalSpecialist":
            ranges = [180., 360., 540., 720., 900., 1080., 1260., 1440., 1620., 1800.]
            factors = [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            return (ranges, factors)
        else:
            ranges = [360., 720., 1080., 1440., 1800., 2160., 2520., 2880., 3240., 3600.]
            factors = [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            return (ranges, factors)
    if decay_type == 'patient_behavior':
        ranges = [230., 345., 495., 590., 725., 800., 890., 945., 995., 1080., 1140.]
        factors = [1., 0.603, 0.345, 0.251, 0.183, 0.135, 0.103, 0.084, 0.059, 0.046, 0.031]
        return (ranges, factors)
    
    if decay_type == 'minimum_standards':
        ranges = [100., 200., 300., 400., 500., 600., 700., 800., 900.]
        factors = [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
        return (ranges, factors)
    
    return ([], [])

def convertTravelMode(travel_mode: str) -> str:
    match travel_mode:
        case "pkw":
            return "driving-car"
        case _:
            return "invalid"


router = APIRouter()

class SpatialAccessRequest(BaseModel):
    # query extent
    supply_level: str
    planning_area: str
    # facility parameters
    facility_type: str
    facility_capacity: str
    # population parameters
    population_type: str
    population_indizes: list[int]|None
    #routing parameters
    travel_mode: str
    decay_type: str

class GridFeature:
    def __init__(self, x: float, y: float, value):
        self.x: float = x
        self.y: float = y
        self.value = value

class GridResponse:
    crs: str
    extend: list[float]
    size: list[int]
    features: list[GridFeature]

    def __init__(self, features, crs, extend, size):
        self.features = features
        self.extend = extend
        self.size = size
        self.crs = crs

@router.post("/grid")
async def spatial_access_api(req: SpatialAccessRequest):
    query = getPlanningArea(req.supply_level, req.planning_area)
    if query is None:
        return {"error": "invalid request"}
    buffer_query = query.buffer(0.2)

    t1 = time.time()
    if req.population_indizes is None:
        points, utm_points, weights = get_population(buffer_query)
    else:
        points, utm_points, weights = get_population(buffer_query, req.population_type, req.population_indizes)
    t2 = time.time()
    print(f"time to load population: {t2-t1}")
    facility_points, facility_weights = getFacilities(buffer_query, req.supply_level, req.facility_type, req.facility_capacity)
    ranges, range_factors = getDistanceDecay(req.travel_mode, req.decay_type, req.supply_level, req.facility_type)
    travel_mode = convertTravelMode(req.travel_mode)

    task = asyncio.create_task(calcFCA(
        points, weights, facility_points, facility_weights, ranges, range_factors, "isochrones", travel_mode))

    features: list[GridFeature] = []
    minx, miny, maxx, maxy = get_extent(utm_points)

    accessibilities = await task

    values = []
    for i, p in enumerate(utm_points):
        point = points[i]
        if not contains_xy(query, point[0], point[1]):
            continue
        access: float = float(accessibilities[i])
        features.append(GridFeature(p[0], p[1], {
            "accessibility": access
        }))
        values.append((access, Point(p[0], p[1])))

    extend = [minx-50, miny-50, maxx+50, maxy+50]
    dx = extend[2] - extend[0]
    dy = extend[3] - extend[1]
    size = [int(dx/100), int(dy/100)]

    crs = "EPSG:25832"

    # # test geosever
    # add_results(values)

    # geo = open_conncection(config.GEOSERVER_URL, 'admin', 'geoserver')
    # add_featurestore(geo, "access_data", "demo", "access")

    return {"features": features, "crs": crs, "extend": extend, "size": size}