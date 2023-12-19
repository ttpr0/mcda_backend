# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon, contains_xy, from_wkb
import json
import os
import string
import random
import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import insert, delete
from geoalchemy2.shape import from_shape

import config
from models import ENGINE, get_table


def insertAdminUser() -> None:
    users = [
        ("dvan@admin.org", "password")
    ]
    with Session(ENGINE) as session:
        user_table = get_table("users")
        if user_table is None:
            return
        for user in users:
            email = user[0]
            password = user[1]
            # generare password salt
            letters = string.ascii_lowercase
            salt = ''.join(random.choice(letters) for i in range(10))

            # hash password+salt
            password_bytes = ''.join([password, salt]).encode()
            h = hashlib.sha256(password_bytes).hexdigest()
            stmt = insert(user_table).values(email=email, password_salt=salt, password_hash=h)
            session.execute(stmt)
        session.commit()


def insertPlanningAreas() -> None:
    area_table = get_table("planning_areas")
    if area_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(area_table).where()
        session.execute(stmt)
        # load physicians data
        for file in os.listdir(config.PLANNING_AREAS_DIR):
            if not os.path.isfile(os.path.join(config.PLANNING_AREAS_DIR, file)):
                continue
            with open(config.PLANNING_AREAS_DIR + "/" + file, "r") as file:
                data = json.loads(file.read())
                for feature in data["features"]:
                    name = feature["attributes"]["HPB"].lower()
                    rings = feature["geometry"]["rings"]
                    polygon = Polygon(rings[0], rings[1:])
                    stmt = insert(area_table).values(name=name, geom=from_shape(polygon))
                    session.execute(stmt)
        session.commit()

def insertPhysicians() -> None:
    loc_table = get_table("physicians_location_based")
    if loc_table is None:
        return
    count_table = get_table("physicians_count_based")
    if count_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(loc_table).where()
        session.execute(stmt)
        stmt = delete(count_table).where()
        session.execute(stmt)
        # load physicians data
        with open(config.SPATIAL_ACCESS_DIR + "/outpatient_physicians_location_based.geojson", "r") as file:
            data = json.loads(file.read())
            vals = []
            for feature in data["features"]:
                props = feature["properties"]
                point = Point(feature["geometry"]["coordinates"])
                typ_id = int(props["TYP_ID"])
                detail_id = int(props["DETAIL_ID_1"])
                vals.append({
                    "point": from_shape(point),
                    "TYP_ID": typ_id,
                    "DETAIL_ID": detail_id,
                    "count": 1,
                })
            stmt = insert(loc_table).values(vals)
            session.execute(stmt)
        with open(config.SPATIAL_ACCESS_DIR + "/outpatient_physician_location_specialist_count.geojson", "r") as file:
            data = json.loads(file.read())
            vals = []
            for feature in data["features"]:
                props = feature["properties"]
                point = Point(feature["geometry"]["coordinates"])
                typ_id = int(props["TYP_ID"])
                detail_id = int(props["DETAIL_ID_1"])
                vbe_sum = float(props["VBE_Sum"])
                pys_count = float(props["Pys_count"])
                vals.append({
                    "point": from_shape(point),
                    "TYP_ID": typ_id,
                    "DETAIL_ID": detail_id,
                    "VBE_Sum": vbe_sum,
                    "Pys_Count": pys_count,
                })
            stmt = insert(count_table).values(vals)
            session.execute(stmt)
        session.commit()

def insertSupplyLevels() -> None:
    supply_levels = [
        ('generalPhysician', 100),
        ('generalSpecialist', 200),
        ('specializedSpecialist', 300),
        ('lowerSaxony', 400)
    ]
    sup_table = get_table("supply_level_list")
    if sup_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(sup_table).where()
        session.execute(stmt)
        # load physicians data
        for sl in supply_levels:
            stmt = insert(sup_table).values(name=sl[0], TYP_ID=sl[1])
            session.execute(stmt)
        session.commit()

def insertPhysiciansList() -> None:
    physicians = [
        ("general_physician", 100, 100),
        ("augenarzte", 200, 205),
        ("surgeon", 200, 212),
        ("frauenarzte", 200, 235),
        ("dermatologist", 200, 225),
        ("hno_arzte", 200, 220),
        ("paediatrician", 200, 245),
        ("neurologist", 200, 230),
        ("psychotherapist", 200, 250),
        ("urologist", 200, 240),
        ("internisten", 300, 302),
        ("jugendpsychiater", 300, 303),
        ("radiologen", 300, 304),
        ("anasthesisten", 300, 301)
    ]
    phys_table = get_table("physicians_list")
    if phys_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(phys_table).where()
        session.execute(stmt)
        # load physicians data
        for sl in physicians:
            stmt = insert(phys_table).values(name=sl[0], TYP_ID=sl[1], DETAIL_ID=sl[2])
            session.execute(stmt)
        session.commit()

def insertPopulation() -> None:
    pop_table = get_table("population")
    if pop_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(pop_table).where()
        session.execute(stmt)
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
                attr["std_00_09"] = int(float(tokens[index_stnd00_09].replace(",", ".")))
                attr["std_10_19"] = int(float(tokens[index_stnd10_19].replace(",", ".")))
                attr["std_20_39"] = int(float(tokens[index_stnd20_39].replace(",", ".")))
                attr["std_40_59"] = int(float(tokens[index_stnd40_59].replace(",", ".")))
                attr["std_60_79"] = int(float(tokens[index_stnd60_79].replace(",", ".")))
                attr["std_80x"] = int(float(tokens[index_stnd80x].replace(",", ".")))
                attr["ksc_00_02"] = int(float(tokens[index_kisc00_02].replace(",", ".")))
                attr["ksc_03_05"] = int(float(tokens[index_kisc03_05].replace(",", ".")))
                attr["ksc_06_09"] = int(float(tokens[index_kisc06_09].replace(",", ".")))
                attr["ksc_10_14"] = int(float(tokens[index_kisc10_14].replace(",", ".")))
                attr["ksc_15_17"] = int(float(tokens[index_kisc15_17].replace(",", ".")))
                attr["ksc_18_19"] = int(float(tokens[index_kisc18_19].replace(",", ".")))
                attr["ksc_20x"] = int(float(tokens[index_kisc20x].replace(",", ".")))

                stmt = insert(pop_table).values(**attr)
                session.execute(stmt)
        session.commit()

def insertFacilities():
    facilities = ["clinic", "dermatologist", "discounter", "general_physician", "gynaecologist", "neurologist",
                  "nursery", "ophthalmologist", "other_local_supply", "otolaryngologist", "paediatrician",
                  "pharmacy", "primary_school", "psychotherapist", "secondary_school_1", "secondary_school_2",
                  "supermarket", "surgeon", "urologist"]
    facil_table = get_table("facilities")
    if facil_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(facil_table).where()
        session.execute(stmt)
        for facility in facilities:
            with open(config.FACILITY_DIR + "/" + facility + ".geojson", "r") as file:
                data = json.loads(file.read())
                vals = []
                for feature in data["features"]:
                    weight = random.randrange(0, 100, 1)
                    point = Point(feature["geometry"]["coordinates"])
                    vals.append({
                        "group": facility,
                        "point": from_shape(point),
                        "wgs_x": point.x,
                        "wgs_y": point.y,
                        "weight": weight,
                    })
                stmt = insert(facil_table).values(vals)
                session.execute(stmt)
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