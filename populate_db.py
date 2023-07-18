# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon, contains_xy, from_wkb
import json
import os
import string
import random
import hashlib
from sqlalchemy.orm import Session

import config
from models import engine, PlanningArea, PhysiciansLocationBased, PhysiciansCountBased, SupplyLevelList, PhysiciansList, User, Population, Facility


def insertAdminUser() -> None:
    users = [
        ("dvan@admin.org", "password")
    ]
    with Session(engine) as session:
        for user in users:
            email = user[0]
            password = user[1]
            # generare password salt
            letters = string.ascii_lowercase
            salt = ''.join(random.choice(letters) for i in range(10))

            # hash password+salt
            password_bytes = ''.join([password, salt]).encode()
            h = hashlib.sha256(password_bytes).hexdigest()
            session.add(User(email, salt, h))
        session.commit()


def insertPlanningAreas() -> None:
    with Session(engine) as session:
        session.query(PlanningArea).delete()
        # load physicians data
        for file in os.listdir(config.PLANNING_AREAS_DIR):
            if not os.path.isfile(os.path.join(config.PLANNING_AREAS_DIR, file)):
                continue
            with open(config.PLANNING_AREAS_DIR + "/" + file, "r") as file:
                data = json.loads(file.read())
                for feature in data["features"]:
                    name = feature["attributes"]["HPB"]
                    rings = feature["geometry"]["rings"]
                    polygon = Polygon(rings[0], rings[1:])
                    session.add(PlanningArea(name, polygon))
        session.commit()

def insertPhysicians() -> None:
    with Session(engine) as session:
        session.query(PhysiciansLocationBased).delete()
        session.query(PhysiciansCountBased).delete()
        # load physicians data
        with open(config.SPATIAL_ACCESS_DIR + "/outpatient_physicians_location_based.geojson", "r") as file:
            data = json.loads(file.read())
            for feature in data["features"]:
                props = feature["properties"]
                point = Point(feature["geometry"]["coordinates"])
                typ_id = int(props["TYP_ID"])
                detail_id = int(props["DETAIL_ID_1"])
                session.add(PhysiciansLocationBased(point, typ_id, detail_id))
        with open(config.SPATIAL_ACCESS_DIR + "/outpatient_physician_location_specialist_count.geojson", "r") as file:
            data = json.loads(file.read())
            for feature in data["features"]:
                props = feature["properties"]
                point = Point(feature["geometry"]["coordinates"])
                typ_id = int(props["TYP_ID"])
                detail_id = int(props["DETAIL_ID_1"])
                vbe_sum = float(props["VBE_Sum"])
                pys_count = float(props["Pys_count"])
                session.add(PhysiciansCountBased(point, typ_id, detail_id, vbe_sum, pys_count))
        session.commit()

def insertSupplyLevels() -> None:
    supply_levels = [
        ('Allgemeine Ärzte', 100),
        ('Spezialisten', 200),
        ('spezielle Spezialisten', 300)
    ]
    with Session(engine) as session:
        session.query(SupplyLevelList).delete()
        # load physicians data
        for sl in supply_levels:
            session.add(SupplyLevelList(sl[0], sl[1]))
        session.commit()

def insertPhysiciansList() -> None:
    physicians = [
        ("Hausärzte", 100, 100),
        ("Augenärzte", 200, 205),
        ("Chirurgen und Orthopäden", 200, 212),
        ("Frauenärzte", 200, 235),
        ("Hautärzte", 200, 225),
        ("HNO-Ärzte", 200, 220),
        ("Kinderärzte", 200, 245),
        ("Nervenärzte", 200, 230),
        ("Psychotherapeuten", 200, 250),
        ("Urologen", 200, 240),
        ("fachärztlich tätige Internisten", 300, 302),
        ("Kinder- und Jugendpsychiater", 300, 303),
        ("Radiologen", 300, 304),
        ("Anästhesisten", 300, 301)
    ]
    with Session(engine) as session:
        session.query(PhysiciansList).delete()
        # load physicians data
        for sl in physicians:
            session.add(PhysiciansList(sl[0], sl[1], sl[2]))
        session.commit()

def insertPopulation() -> None:
    with Session(engine) as session:
        session.query(Population).delete()
        # load population data
        with open(config.POPULATION_FILE, 'r') as file:
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

                point: Point = from_wkb(bytes.fromhex(tokens[index_geom]))
                utm_point: Point = from_wkb(bytes.fromhex(tokens[index_geom_utm]))
                attr = {
                    "point": point.wkt,
                    "wgs_x": point.x,
                    "wgs_y": point.y,
                    "utm_x": utm_point.x,
                    "utm_y": utm_point.y,
                }
                attr["ew_gesamt"] = int(float(tokens[index_ew_gesamt].replace(",", ".")))
                attr["stnd00_09"] = int(float(tokens[index_stnd00_09].replace(",", ".")))
                attr["stnd10_19"] = int(float(tokens[index_stnd10_19].replace(",", ".")))
                attr["stnd20_39"] = int(float(tokens[index_stnd20_39].replace(",", ".")))
                attr["stnd40_59"] = int(float(tokens[index_stnd40_59].replace(",", ".")))
                attr["stnd60_79"] = int(float(tokens[index_stnd60_79].replace(",", ".")))
                attr["stnd80x"] = int(float(tokens[index_stnd80x].replace(",", ".")))
                attr["kisc00_02"] = int(float(tokens[index_kisc00_02].replace(",", ".")))
                attr["kisc03_05"] = int(float(tokens[index_kisc03_05].replace(",", ".")))
                attr["kisc06_09"] = int(float(tokens[index_kisc06_09].replace(",", ".")))
                attr["kisc10_14"] = int(float(tokens[index_kisc10_14].replace(",", ".")))
                attr["kisc15_17"] = int(float(tokens[index_kisc15_17].replace(",", ".")))
                attr["kisc18_19"] = int(float(tokens[index_kisc18_19].replace(",", ".")))
                attr["kisc20x"] = int(float(tokens[index_kisc20x].replace(",", ".")))

                session.add(Population(**attr))
        session.commit()

def insertFacilities():
    facilities = ["clinic", "dermatologist", "discounter", "general_physician", "gynaecologist", "neurologist",
                  "nursery", "ophthalmologist", "other_local_supply", "otolaryngologist", "paediatrician",
                  "pharmacy", "primary_school", "psychotherapist", "secondary_school_1", "secondary_school_2",
                  "supermarket", "surgeon", "urologist"]
    with Session(engine) as session:
        for facility in facilities:
            with open(config.FACILITY_DIR + "/" + facility + ".geojson", "r") as file:
                data = json.loads(file.read())
                for feature in data["features"]:
                    weight = random.randrange(0, 100, 1)
                    point = Point(feature["geometry"]["coordinates"])
                    session.add(Facility(facility, point, weight))
        session.commit()


if __name__ == "__main__":
    print("start inserting Physicians")
    insertPhysicians()
    print("start inserting Planning Areas")
    insertPlanningAreas()
    print("start inserting Physician Lists")
    insertPhysiciansList()
    print("start inserting Supply Levels")
    insertSupplyLevels()
    print("start inserting Admin User")
    insertAdminUser()
    print("start inserting Population")
    # insertPopulation()
    print("start inserting Facilities")
    insertFacilities()