# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import select
from geoalchemy2 import Geometry
from sqlalchemy.orm import Session
from shapely import Point, Polygon, from_wkb, STRtree

from . import ENGINE, get_table

# from . import Base

# class Population(Base):
#     __tablename__ = "population"

#     pid = Column("pid", Integer, primary_key=True, autoincrement=True)
#     point = Column("point", Geometry('POINT'), index=True)
#     wgs_x = Column("wgs_x", Float)
#     wgs_y = Column("wgs_y", Float)
#     utm_x = Column("utm_x", Float)
#     utm_y = Column("utm_y", Float)

#     ew_gesamt = Column("ew_gesamt", Integer)
#     stnd00_09 = Column("std_00_09", Integer)
#     stnd10_19 = Column("std_10_19", Integer)
#     stnd20_39 = Column("std_20_39", Integer)
#     stnd40_59 = Column("std_40_59", Integer)
#     stnd60_79 = Column("std_60_79", Integer)
#     stnd80x = Column("std_80x", Integer)
#     kisc00_02 = Column("ksc_00_02", Integer)
#     kisc03_05 = Column("ksc_03_05", Integer)
#     kisc06_09 = Column("ksc_06_09", Integer)
#     kisc10_14 = Column("ksc_10_14", Integer)
#     kisc15_17 = Column("ksc_15_17", Integer)
#     kisc18_19 = Column("ksc_18_19", Integer)
#     kisc20x = Column("ksc_20x", Integer)


#     def __init__(self, **kwargs):
#         for key, value in kwargs.items():
#             setattr(self, key, value)
    
#     def __repr__(self):
#         return f"User {self.pid}"


class PopulationPoint:
    __slots__ = ('index', 'point', 'utm_point', 'population_count', 'standard_population', 'kita_schul_population')
    point: Point
    utm_point: Point
    population_count: int
    standard_population: list[int]
    kita_schul_population: list[int]

    def __init__(self, point: Point, utm_point: Point, count: int, standard: list[int], kita_schul: list[int]):
        self.point = point
        self.utm_point = utm_point
        self.population_count = count
        self.standard_population = standard
        self.kita_schul_population = kita_schul

    def getPopulationCount(self) -> int:
        return self.population_count

    def getStandardPopulation(self, indizes: list[int]) -> int:
        count = 0
        for key in indizes:
            count += self.standard_population[key]
        return count

    def getKitaSchulPopulation(self, indizes: list[int]) -> int:
        count = 0
        for key in indizes:
            count += self.kita_schul_population[key]
        return count

class PopulationProvider:
    def __init__(self):
        self.p_points: list[PopulationPoint] = []
        self.points: list[Point] = []
        self.index: STRtree | None = None

    def addPopulationPoint(self, point: PopulationPoint):
        self.points.append(point.point)
        self.p_points.append(point)

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
                weight = p_point.getStandardPopulation(indizes)
            elif typ == 'kita_schul':
                weight = p_point.getKitaSchulPopulation(indizes)
            else:
                weight = p_point.getPopulationCount()
            if weight <= 0:
                continue
            locations.append((p_point.point.x, p_point.point.y))
            utm_locations.append((p_point.utm_point.x, p_point.utm_point.y))
            weights.append(weight)
        return locations, utm_locations, weights

    
POPULATION: PopulationProvider

def load_population(filename: str):
    global POPULATION
    POPULATION = PopulationProvider()
    with open(filename, 'r') as file:
        delimiter = ';'
        line = file.readline()
        tokens = line.split(delimiter)

        # population indices
        index_ew_gesamt = -1
        index_stnd00_09 = -1
        index_stnd10_19 = -1
        index_stnd20_39 = -1
        index_stnd40_59 = -1
        index_stnd60_79 = -1
        index_stnd80x = -1
        index_kisc00_02 = -1
        index_kisc03_05 = -1
        index_kisc06_09 = -1
        index_kisc10_14 = -1
        index_kisc15_17 = -1
        index_kisc18_19 = -1
        index_kisc20x = -1

        # geom indices
        index_geom = -1
        index_geom_utm = -1

        for i, token in enumerate(tokens):
            if token == "EW_GESAMT":
                index_ew_gesamt = i
            if token == "GEOM":
                index_geom = i
            if token == "GEOM_UTM":
                index_geom_utm = i
            if token == "STND00_09":
                index_stnd00_09 = i
            if token == "STND10_19":
                index_stnd10_19 = i
            if token == "STND20_39":
                index_stnd20_39 = i
            if token == "STND40_59":
                index_stnd40_59 = i
            if token == "STND60_79":
                index_stnd60_79 = i
            if token == "STND80X":
                index_stnd80x = i
            if token == "KITA_SCHUL":
                index_kisc00_02 = i
            if token == "KITA_SC_01":
                index_kisc03_05 = i
            if token == "KITA_SC_02":
                index_kisc06_09 = i
            if token == "KITA_SC_03":
                index_kisc10_14 = i
            if token == "KITA_SC_04":
                index_kisc15_17 = i
            if token == "KITA_SC_05":
                index_kisc18_19 = i
            if token == "KITA_SC_06":
                index_kisc20x = i
        
        while True:
            line = file.readline()
            if not line:
                break

            tokens = line.split(delimiter)
            ew_gesamt = int(float(tokens[index_ew_gesamt].replace(",", ".")))
            std_00_09 = int(float(tokens[index_stnd00_09].replace(",", ".")))
            std_10_19 = int(float(tokens[index_stnd10_19].replace(",", ".")))
            std_20_39 = int(float(tokens[index_stnd20_39].replace(",", ".")))
            std_40_59 = int(float(tokens[index_stnd40_59].replace(",", ".")))
            std_60_79 = int(float(tokens[index_stnd60_79].replace(",", ".")))
            std_80x = int(float(tokens[index_stnd80x].replace(",", ".")))
            ksc_00_02 = int(float(tokens[index_kisc00_02].replace(",", ".")))
            ksc_03_05 = int(float(tokens[index_kisc03_05].replace(",", ".")))
            ksc_06_09 = int(float(tokens[index_kisc06_09].replace(",", ".")))
            ksc_10_14 = int(float(tokens[index_kisc10_14].replace(",", ".")))
            ksc_15_17 = int(float(tokens[index_kisc15_17].replace(",", ".")))
            ksc_18_19 = int(float(tokens[index_kisc18_19].replace(",", ".")))
            ksc_20x = int(float(tokens[index_kisc20x].replace(",", ".")))
            standard_population = [std_00_09, std_10_19, std_20_39, std_40_59, std_60_79, std_80x]
            kita_schul_population = [ksc_00_02, ksc_03_05, ksc_06_09, ksc_10_14, ksc_15_17, ksc_18_19, ksc_20x]

            point: Point = from_wkb(bytes.fromhex(tokens[index_geom]))
            utm_point: Point = from_wkb(bytes.fromhex(tokens[index_geom_utm]))
            attributes: PopulationPoint = PopulationPoint(point, utm_point, ew_gesamt, standard_population, kita_schul_population)
            POPULATION.addPopulationPoint(attributes)
        POPULATION.generateIndex()

def get_population(query: Polygon, typ: str = 'standard_all', indizes: list[int] = []) -> tuple[list[tuple[float, float]], list[tuple[float, float]], list[int]]:
    global POPULATION
    return POPULATION.getPopulationInEnvelope(query, typ, indizes)

def convert_population_keys(typ: str, keys: list[str]) -> list[int]|None:
    indizes = []
    if typ == "standard":
        for key in keys:
            match key:
                case "std_00_09":
                    indizes.append(0)
                case "std_10_19":
                    indizes.append(1)
                case "std_20_39":
                    indizes.append(2)
                case "std_40_59":
                    indizes.append(3)
                case "std_60_79":
                    indizes.append(4)
                case "std_80x":
                    indizes.append(5)
                case _:
                    return None
    elif typ == "kita_schul":
        for key in keys:
            match key:
                case "ksc_00_02":
                    indizes.append(0)
                case "ksc_03_05":
                    indizes.append(1)
                case "ksc_06_09":
                    indizes.append(2)
                case "ksc_10_14":
                    indizes.append(3)
                case "ksc_15_17":
                    indizes.append(4)
                case "ksc_18_19":
                    indizes.append(5)
                case "ksc_20x":
                    indizes.append(6)
                case _:
                    return None
    return indizes

# def get_population(query: Polygon, typ: str = 'standard_all', indizes: list[int] = []) -> tuple[list[tuple[float, float]], list[tuple[float, float]], list[int]]:
#     locations: list[tuple[float, float]] = []
#     utm_locations: list[tuple[float, float]] = []
#     weights: list[int] = []
#     with Session(ENGINE) as session:
#         population_fields: list[str] = []
#         if typ == 'standard':
#             fields = ["std_00_09", "std_10_19", "std_20_39", "std_40_59", "std_60_79", "std_80x"]
#             for index in indizes:
#                 population_fields.append(fields[index])
#         elif typ == 'kita_schul':
#             fields = ["ksc_00_02", "ksc_03_05", "ksc_06_09", "ksc_10_14", "ksc_15_17", "ksc_18_19", "ksc_20x"]
#             for index in indizes:
#                 population_fields.append(fields[index])
#         else:
#             population_fields.append("ew_gesamt")
#         stmt = select(Population.wgs_x, Population.wgs_y, Population.utm_x, Population.utm_y, *[getattr(Population, field) for field in population_fields]).where(Population.point.ST_Within(query.wkt))
#         rows = session.execute(stmt).fetchall()
#         for row in rows:
#             wgs_x: float = row[0]
#             wgs_y: float = row[1]
#             utm_x: float = row[2]
#             utm_y: float = row[3]
#             locations.append((wgs_x, wgs_y))
#             utm_locations.append((utm_x, utm_y))
#             weight = 0
#             for val in row[4:]:
#                 weight += val
#             weights.append(weight)
#     return locations, utm_locations, weights


POPULATION_VALUES = {
    "standard": {
        "text": "population.groups.standard",
        "items": {
            "std_00_09": (0, 9),
            "std_10_19": (10, 19),
            "std_20_39": (20, 39),
            "std_40_59": (40, 59),
            "std_60_79": (60, 79),
            "std_80x": (80,)
        }
    },
    "kita_schul": {
        "text": "population.groups.kitaSchul",
        "items": {
            "ksc_00_02": (0, 2),
            "ksc_03_05": (3, 5),
            "ksc_06_09": (6, 9),
            "ksc_10_14": (10, 14),
            "ksc_15_17": (15, 17),
            "ksc_18_19": (18, 19),
            "ksc_20x": (20,)
        }
    },
}

def get_available_population():
    return POPULATION_VALUES
