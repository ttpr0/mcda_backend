# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon, contains_xy, from_wkb
import json
import os
import string
import random
import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import insert, delete, Column, Integer
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape

from models import ENGINE, get_table, create_table

POPULATION_FILE = "./files/population.csv"
FACILITY_DIR = "./files/facilities"
SPATIAL_ACCESS_DIR = "./files/physicians"
PLANNING_AREAS_DIR = "./files/planning_areas"

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
            stmt = insert(user_table).values(EMAIL=email, PASSWORD_SALT=salt, PASSWORD_HASH=h)
            session.execute(stmt)
        session.commit()

def insertPlanningAreas() -> None:
    # additional data
    mapping = {
        "aurich": {"i18n_key": "planningAreas.aurich", "supply_levels": [100, 200]},
        "emden": {"i18n_key": "planningAreas.emden", "supply_levels": [100, 200]},
        "jever": {"i18n_key": "planningAreas.jever", "supply_levels": [100, 200]},
        "norden": {"i18n_key": "planningAreas.norden", "supply_levels": [100, 200]},
        "varel": {"i18n_key": "planningAreas.varel", "supply_levels": [100, 200]},
        "wilhelmshaven": {"i18n_key": "planningAreas.wilhelmshaven", "supply_levels": [100, 200]},
        "wittmund": {"i18n_key": "planningAreas.wittmund", "supply_levels": [100, 200]},
        "niedersachsen": {"i18n_key": "planningAreas.niedersachsen", "supply_levels": [400]},
        "kv_bezirk": {"i18n_key": "planningAreas.kv_bezirk", "supply_levels": [400]},
    }
    # inserting data
    area_table = get_table("planning_areas")
    if area_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(area_table).where()
        session.execute(stmt)
        for file in os.listdir(PLANNING_AREAS_DIR):
            if not os.path.isfile(os.path.join(PLANNING_AREAS_DIR, file)):
                continue
            with open(PLANNING_AREAS_DIR + "/" + file, "r") as file:
                data = json.loads(file.read())
                for feature in data["features"]:
                    name = feature["attributes"]["HPB"].lower()
                    rings = feature["geometry"]["rings"]
                    polygon = Polygon(rings[0], rings[1:])
                    if name not in mapping:
                        continue
                    i18n_key = mapping[name]["i18n_key"]
                    level_ids = mapping[name]["supply_levels"]
                    stmt = insert(area_table).values(NAME=name, I18N_KEY=i18n_key, SUPPLY_LEVEL_IDS=level_ids, GEOMETRY=from_shape(polygon))
                    session.execute(stmt)
        session.commit()

def insertPhysicians() -> None:
    loc_table = get_table("physicians_locations")
    if loc_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(loc_table).where()
        session.execute(stmt)
        # load physicians data
        with open(SPATIAL_ACCESS_DIR + "/outpatient_physician_location_specialist_count.geojson", "r") as file:
            data = json.loads(file.read())
            vals = []
            for feature in data["features"]:
                props = feature["properties"]
                point = Point(feature["geometry"]["coordinates"])
                physician_id = int(props["DETAIL_ID_1"])
                vbe_sum = float(props["VBE_Sum"])
                phys_count = float(props["Pys_count"])
                vals.append({
                    "GEOMETRY": from_shape(point),
                    "PHYSICIAN_ID": physician_id,
                    "VBE_VOLUME": vbe_sum,
                    "PHYSICIAN_COUNT": phys_count,
                })
            stmt = insert(loc_table).values(vals)
            session.execute(stmt)
        session.commit()

def insertSupplyLevels() -> None:
    supply_levels = [
        ('generalPhysician', 100, "supplyLevels.generalPhysician", True),
        ('generalSpecialist', 200, "supplyLevels.generalSpecialist", True),
        ('specializedSpecialist', 300, "supplyLevels.specializedSpecialist", False),
        ('lowerSaxony', 400, "supplyLevels.lowerSaxony", True)
    ]
    sup_table = get_table("supply_level_list")
    if sup_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(sup_table).where()
        session.execute(stmt)
        for sl in supply_levels:
            stmt = insert(sup_table).values(NAME=sl[0], I18N_KEY=sl[2], VALID=sl[3], SUPPLY_LEVEL_ID=sl[1])
            session.execute(stmt)
        session.commit()

def insertPhysiciansList() -> None:
    physicians = [
        ("general_physician", "physicians.generalPhysician", [100], 100),
        ("augenarzte", "physicians.augenarzte", [200, 400], 205),
        ("surgeon", "physicians.surgeon", [200, 400], 212),
        ("frauenarzte", "physicians.frauenarzte", [200, 400], 235),
        ("dermatologist", "physicians.dermatologist", [200, 400], 225),
        ("hno_arzte", "physicians.hnoArzte", [200, 400], 220),
        ("paediatrician", "physicians.paediatrician", [200, 400], 245),
        ("neurologist", "physicians.neurologist", [200, 400], 230),
        ("psychotherapist", "physicians.psychotherapist", [200, 400], 250),
        ("urologist", "physicians.urologist", [200, 400], 240),
        ("internisten", "physicians.internisten", [300, 400], 302),
        ("jugendpsychiater", "physicians.jugendpsychiater", [300, 400], 303),
        ("radiologen", "physicians.radiologen", [300, 400], 304),
        ("anasthesisten", "physicians.anasthesisten", [300, 400], 301)
    ]
    phys_table = get_table("physicians_list")
    if phys_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(phys_table).where()
        session.execute(stmt)
        for sl in physicians:
            stmt = insert(phys_table).values(NAME=sl[0], I18N_KEY=sl[1], SUPPLY_LEVEL_IDS=sl[2], PHYSICIAN_ID=sl[3])
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
        with open(POPULATION_FILE, 'r') as file:
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

def insertFacilityGroups() -> None:
    groups = [
        ("localSupply", "localSupply.text", 100, None),
        ("health", "health.text", 200, None),
        ("physicians", "health.physicians.text", 201, 200),
        ("education", "education.text", 300, None),
    ]
    group_table = get_table("facilities_groups")
    if group_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(group_table).where()
        session.execute(stmt)
        for sl in groups:
            stmt = insert(group_table).values(NAME=sl[0], I18N_KEY=sl[1], GROUP_ID=sl[2], SUPER_GROUP_ID=sl[3])
            session.execute(stmt)
        session.commit()

def insertFacilities():
    facilities = {
        "supermarket": {"i18n_key": "localSupply.supermarket", "tooltip_key": None, "group_id": 100},
        "discounter": {"i18n_key": "localSupply.discounter", "tooltip_key": None, "group_id": 100},
        "other_local_supply": {"i18n_key": "localSupply.otherLocalSupply", "tooltip_key": "tooltip.otherLocalSupply", "group_id": 100},
        "clinic": {"i18n_key": "health.clinic", "tooltip_key": None, "group_id": 200},
        "pharmacy": {"i18n_key": "health.pharmacy", "tooltip_key": None, "group_id": 200},
        "dermatologist": {"i18n_key": "health.physicians.dermatologist", "tooltip_key": None, "group_id": 201},
        "general_physician": {"i18n_key": "health.physicians.generalPhysicians", "tooltip_key": None, "group_id": 201},
        "gynaecologist": {"i18n_key": "health.physicians.gynaecologist", "tooltip_key": None, "group_id": 201},
        "neurologist": {"i18n_key": "health.physicians.neurologist", "tooltip_key": None, "group_id": 201},
        "ophthalmologist": {"i18n_key": "health.physicians.ophthalmologist", "tooltip_key": None, "group_id": 201},
        "otolaryngologist": {"i18n_key": "health.physicians.otolaryngologist", "tooltip_key": None, "group_id": 201},
        "paediatrician": {"i18n_key": "health.physicians.paediatrician", "tooltip_key": None, "group_id": 201},
        "psychotherapist": {"i18n_key": "health.physicians.psychotherapists", "tooltip_key": None, "group_id": 201},
        "surgeon": {"i18n_key": "health.physicians.surgeon", "tooltip_key": None, "group_id": 201},
        "urologist": {"i18n_key": "health.physicians.urologists", "tooltip_key": None, "group_id": 201},
        "nursery": {"i18n_key": "education.nursery", "tooltip_key": "tooltip.nursery", "group_id": 300},
        "primary_school": {"i18n_key": "education.primarySchool", "tooltip_key": "tooltip.primarySchool", "group_id": 300},
        "secondary_school_1": {"i18n_key": "education.secondarySchool1", "tooltip_key": "tooltip.secondarySchool1", "group_id": 300},
        "secondary_school_2": {"i18n_key": "education.secondarySchool2", "tooltip_key": "tooltip.secondarySchool2", "group_id": 300},
    }
    # create facility tables
    for facility in facilities:
        table_name = f"facilities_{facility}"
        table_spec = [
            Column("GEOMETRY", Geometry("POINT", srid=4326)),
            Column("WEIGHT", Integer),
        ]
        create_table(table_name, table_spec)

    list_table = get_table("facilities_list")
    if list_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(list_table).where()
        session.execute(stmt)
        for facility in facilities:
            i18n_key = facilities[facility]["i18n_key"]
            tooltip_key = facilities[facility]["tooltip_key"]
            group_id = facilities[facility]["group_id"]
            table_name = f"facilities_{facility}"
            stmt = insert(list_table).values(NAME=facility, I18N_KEY=i18n_key, TOOLTIP_KEY=tooltip_key, GROUP_ID=group_id, TABLE_NAME=table_name, GEOMETRY_COLUMN="GEOMETRY", WEIGHT_COLUMN="WEIGHT")
            session.execute(stmt)
            facility_table = get_table(table_name)
            if facility_table is None:
                raise ValueError("invalid condition.")
            with open(FACILITY_DIR + "/" + facility + ".geojson", "r") as file:
                data = json.loads(file.read())
                vals = []
                for feature in data["features"]:
                    weight = random.randrange(0, 100, 1)
                    point = Point(feature["geometry"]["coordinates"])
                    vals.append({
                        "GEOMETRY": from_shape(point),
                        "WEIGHT": weight,
                    })
                stmt = insert(facility_table).values(vals)
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
    insertFacilityGroups()
    insertFacilities()