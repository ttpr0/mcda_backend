# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon, from_wkb, STRtree
from sqlalchemy.orm import Session
from sqlalchemy import select
import geoalchemy2

from models import engine, Population

class PopulationAttributes:
    __slots__ = ('index', 'population_count', 'standard_population', 'kita_schul_population')
    index: int
    population_count: int
    standard_population: list[int]
    kita_schul_population: list[int]

    def __init__(self, count: int, standard: list[int], kita_schul: list[int]):
        self.index = 0
        self.population_count = count
        self.standard_population = standard
        self.kita_schul_population = kita_schul

    def getPopulationCount(self) -> int:
        return self.population_count

    def getStandardPopulation(self, indizes: list[int]) -> int:
        count = 0
        for i in range(len(indizes)):
            count += self.standard_population[indizes[i]]
        return count

    def getKitaSchulPopulation(self, indizes: list[int]) -> int:
        count = 0
        for i in range(len(indizes)):
            count += self.kita_schul_population[indizes[i]]
        return count


class PopulationPoint:
    __slots__ = ('point', 'utm_point', 'attributes', 'weight')
    point: Point
    utm_point: Point
    attributes: PopulationAttributes
    weight: int

    def __init__(self, point: Point, utm_point: Point, attributes: PopulationAttributes):
        self.point = point
        self.utm_point = utm_point
        self.attributes = attributes
        self.weight = 0

class PopulationProvider:
    def __init__(self):
        self.p_points: list[PopulationPoint] = []
        self.points: list[Point] = []
        self.attributes: list[PopulationAttributes] = []
        self.index: STRtree | None = None

    def addPopulationPoint(self, point: Point, utm_point: Point, attributes: PopulationAttributes):
        index: int = len(self.points)
        attributes.index = index
        self.points.append(point)
        self.attributes.append(attributes)
        self.p_points.append(PopulationPoint(point, utm_point, attributes))

    def getPoint(self, index: int) -> PopulationPoint:
        return self.p_points[index]

    def pointCount(self) -> int:
        return len(self.points)

    def generateIndex(self):
        self.index = STRtree(self.points)

    def getPointsInEnvelope(self, query: Polygon) -> list[PopulationPoint]:
        if self.index == None:
            return []
        return [self.p_points[idx] for idx in self.index.query(query)]

    def getPopulationInEnvelope(self, query: Polygon, typ: str = 'standard_all', indizes: list[int] = []) -> tuple[list[tuple[float, float]], list[tuple[float, float]], list[int]]:
        locations: list[tuple[float, float]] = []
        utm_locations: list[tuple[float, float]] = []
        weights: list[int] = []
        if self.index is None:
            return locations, utm_locations, weights
        for idx in self.index.query(query):
            p_point: PopulationPoint = self.p_points[idx]
            weight: int
            if typ == 'standard':
                weight = p_point.attributes.getStandardPopulation(indizes)
            elif typ == 'kita_schul':
                weight = p_point.attributes.getKitaSchulPopulation(indizes)
            else:
                weight = p_point.attributes.getPopulationCount()
            if weight <= 0:
                continue
            locations.append((p_point.point.x, p_point.point.y))
            utm_locations.append((p_point.utm_point.x, p_point.utm_point.y))
            weights.append(weight)
        return locations, utm_locations, weights

    
POPULATION: PopulationProvider

def load_population(filename: str):
    pass
    # with open(filename, 'r') as file:
    #     delimiter = ';'
    #     line = file.readline()
    #     tokens = line.split(delimiter)

    #     # population indices
    #     index_ew_gesamt = -1
    #     index_stnd00_09 = -1
    #     index_stnd10_19 = -1
    #     index_stnd20_39 = -1
    #     index_stnd40_59 = -1
    #     index_stnd60_79 = -1
    #     index_stnd80x = -1
    #     index_kisc00_02 = -1
    #     index_kisc03_05 = -1
    #     index_kisc06_09 = -1
    #     index_kisc10_14 = -1
    #     index_kisc15_17 = -1
    #     index_kisc18_19 = -1
    #     index_kisc20x = -1

    #     # geom indices
    #     index_geom = -1
    #     index_geom_utm = -1

    #     for i, token in enumerate(tokens):
    #         if token == "EW_GESAMT":
    #             index_ew_gesamt = i
    #         if token == "GEOM":
    #             index_geom = i
    #         if token == "GEOM_UTM":
    #             index_geom_utm = i
    #         if token == "STND00_09":
    #             index_stnd00_09 = i
    #         if token == "STND10_19":
    #             index_stnd10_19 = i
    #         if token == "STND20_39":
    #             index_stnd20_39 = i
    #         if token == "STND40_59":
    #             index_stnd40_59 = i
    #         if token == "STND60_79":
    #             index_stnd60_79 = i
    #         if token == "STND80X":
    #             index_stnd80x = i
    #         if token == "KITA_SCHUL":
    #             index_kisc00_02 = i
    #         if token == "KITA_SC_01":
    #             index_kisc03_05 = i
    #         if token == "KITA_SC_02":
    #             index_kisc06_09 = i
    #         if token == "KITA_SC_03":
    #             index_kisc10_14 = i
    #         if token == "KITA_SC_04":
    #             index_kisc15_17 = i
    #         if token == "KITA_SC_05":
    #             index_kisc18_19 = i
    #         if token == "KITA_SC_06":
    #             index_kisc20x = i
        
    #     POPULATION = PopulationProvider()
    #     while True:
    #         line = file.readline()
    #         if not line:
    #             break

    #         tokens = line.split(delimiter)
    #         ew_gesamt = int(float(tokens[index_ew_gesamt].replace(",", ".")))
    #         stnd00_09 = int(float(tokens[index_stnd00_09].replace(",", ".")))
    #         stnd10_19 = int(float(tokens[index_stnd10_19].replace(",", ".")))
    #         stnd20_39 = int(float(tokens[index_stnd20_39].replace(",", ".")))
    #         stnd40_59 = int(float(tokens[index_stnd40_59].replace(",", ".")))
    #         stnd60_79 = int(float(tokens[index_stnd60_79].replace(",", ".")))
    #         stnd80x = int(float(tokens[index_stnd80x].replace(",", ".")))
    #         kisc00_02 = int(float(tokens[index_kisc00_02].replace(",", ".")))
    #         kisc03_05 = int(float(tokens[index_kisc03_05].replace(",", ".")))
    #         kisc06_09 = int(float(tokens[index_kisc06_09].replace(",", ".")))
    #         kisc10_14 = int(float(tokens[index_kisc10_14].replace(",", ".")))
    #         kisc15_17 = int(float(tokens[index_kisc15_17].replace(",", ".")))
    #         kisc18_19 = int(float(tokens[index_kisc18_19].replace(",", ".")))
    #         kisc20x = int(float(tokens[index_kisc20x].replace(",", ".")))
    #         standard_population = [stnd00_09, stnd10_19, stnd20_39, int(stnd40_59 / 2), int(stnd40_59 / 2), stnd60_79, stnd80x]
    #         kita_schul_population = [kisc00_02, kisc03_05, kisc06_09, kisc10_14, kisc15_17, kisc18_19, kisc20x]

    #         attributes: PopulationAttributes = PopulationAttributes(ew_gesamt, standard_population, kita_schul_population)
    #         point: Point = from_wkb(bytes.fromhex(tokens[index_geom]))
    #         utm_point: Point = from_wkb(bytes.fromhex(tokens[index_geom_utm]))
    #         POPULATION.addPopulationPoint(point, utm_point, attributes)
    #     POPULATION.generateIndex()

# def get_population(query: Polygon, typ: str = 'standard_all', indizes: list[int] = []) -> tuple[list[tuple[float, float]], list[tuple[float, float]], list[int]]:
#     return POPULATION.getPopulationInEnvelope(query, typ, indizes)

def get_population(query: Polygon, typ: str = 'standard_all', indizes: list[int] = []) -> tuple[list[tuple[float, float]], list[tuple[float, float]], list[int]]:
    locations: list[tuple[float, float]] = []
    utm_locations: list[tuple[float, float]] = []
    weights: list[int] = []
    with Session(engine) as session:
        population_fields: list[str] = []
        if typ == 'standard':
            fields = ["stnd00_09", "stnd10_19", "stnd20_39", "stnd40_59", "stnd60_79", "stnd80x"]
            for index in indizes:
                population_fields.append(fields[index])
        elif typ == 'kita_schul':
            fields = ["kisc00_02", "kisc03_05", "kisc06_09", "kisc10_14", "kisc15_17", "kisc18_19", "kisc20x"]
            for index in indizes:
                population_fields.append(fields[index])
        else:
            population_fields.append("ew_gesamt")
        stmt = select(Population.wgs_x, Population.wgs_y, Population.utm_x, Population.utm_y, *[getattr(Population, field) for field in population_fields]).where(Population.point.ST_Within(query.wkt))
        rows = session.execute(stmt).fetchall()
        for row in rows:
            wgs_x: float = row[0]
            wgs_y: float = row[1]
            utm_x: float = row[2]
            utm_y: float = row[3]
            locations.append((wgs_x, wgs_y))
            utm_locations.append((utm_x, utm_y))
            weight = 0
            for val in row[4:]:
                weight += val
            weights.append(weight)
    return locations, utm_locations, weights
