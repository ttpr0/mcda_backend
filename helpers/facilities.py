# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import json
import random
from shapely import Point, Polygon, STRtree
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import engine, Facility as FacilityTable

class Facility:
    points: list[Point]
    weights: list[float]
    index: STRtree

    def __init__(self, points: list[Point], weights: list[float]):
        self.points = points
        self.weights = weights
        self.buildIndex()

    def buildIndex(self):
        self.index = STRtree(self.points)

    def getFacilitiesInEnvelop(self, query: Polygon) -> tuple[list[tuple[float, float]], list[float]]:
        if self.index == None:
            return [], []
        points = []
        weights = []
        idx: int
        for idx in self.index.query(query):
            point: Point = self.points[idx]
            points.append((point.x, point.y))
            weights.append(self.weights[idx])
        return points, weights


FACILITIES: dict[str, Facility] = {}

def load_facilities(path: str):
    pass
    # facilities = ["clinic", "dermatologist", "discounter", "general_physician", "gynaecologist", "neurologist",
    #               "nursery", "ophthalmologist", "other_local_supply", "otolaryngologist", "paediatrician",
    #               "pharmacy", "primary_school", "psychotherapist", "secondary_school_1", "secondary_school_2",
    #               "supermarket", "surgeon", "urologist"]
    
    # for facility in facilities:
    #     with open(path + "/" + facility + ".geojson", "r") as file:
    #         data = json.loads(file.read())
    #         points: list[Point] = []
    #         weights: list[float] = []
    #         for feature in data["features"]:
    #             weights.append(random.randrange(0, 100, 1))
    #             points.append(Point(feature["geometry"]["coordinates"]))
    #         FACILITIES[facility] = Facility(points, weights)

# def get_facility(name: str, envelop: Polygon) -> tuple[list[tuple[float, float]], list[float]]:
#     return FACILITIES[name].getFacilitiesInEnvelop(envelop)

def get_facility(name: str, envelop: Polygon) -> tuple[list[tuple[float, float]], list[float]]:
    locations = []
    weights = []
    with Session(engine) as session:
        stmt = select(FacilityTable.wgs_x, FacilityTable.wgs_y, FacilityTable.weight).where((FacilityTable.group==name) & FacilityTable.point.ST_Within(envelop.wkt))
        rows = session.execute(stmt).fetchall()
        for row in rows:
            wgs_x: float = row[0]
            wgs_y: float = row[1]
            weight: float = row[2]
            locations.append((wgs_x, wgs_y))
            weights.append(weight)
    return locations, weights
