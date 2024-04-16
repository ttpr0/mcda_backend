# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Point, Polygon, contains_xy, from_wkb
import json
import os
import string
import random
import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import insert, delete, Column, Integer, String, Float
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape

from models import ENGINE, get_table, create_table

POPULATION_FILE = "./files/population.csv"
FACILITY_DIR = "./files/facilities"
SPATIAL_ACCESS_DIR = "./files/physicians"
PLANNING_AREAS_DIR = "./files/planning_areas"

def insertAdminUser() -> None:
    users = [
        ("admin", "dvan@admin.org", "admin", "password")
    ]
    with Session(ENGINE) as session:
        user_table = get_table("users")
        if user_table is None:
            return
        for user in users:
            name = user[0]
            email = user[1]
            group = user[2]
            password = user[3]
            # generare password salt
            letters = string.ascii_lowercase
            salt = ''.join(random.choice(letters) for i in range(10))

            # hash password+salt
            password_bytes = ''.join([password, salt]).encode()
            h = hashlib.sha256(password_bytes).hexdigest()
            stmt = insert(user_table).values(username=name ,email=email, group=group, password_salt=salt, password_hash=h)
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
                    name = feature["properties"]["Name"].lower()
                    rings = feature["geometry"]["coordinates"]
                    polygon = Polygon(rings[0], rings[1:])
                    if name not in mapping:
                        continue
                    i18n_key = mapping[name]["i18n_key"]
                    level_ids = mapping[name]["supply_levels"]
                    stmt = insert(area_table).values(name=name, i18n_key=i18n_key, supply_level_ids=level_ids, geometry=from_shape(polygon))
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
                    "geometry": from_shape(point),
                    "physician_id": physician_id,
                    "vbe_volume": vbe_sum,
                    "physician_count": phys_count,
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
            stmt = insert(sup_table).values(name=sl[0], i18n_key=sl[2], valid=sl[3], supply_level_id=sl[1])
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
            stmt = insert(phys_table).values(name=sl[0], i18n_key=sl[1], supply_level_ids=sl[2], physician_id=sl[3])
            session.execute(stmt)
        session.commit()

def insertPopulation() -> None:
    # populations = {
    #     "standard": {
    #         "i18n_key": "population.groups.standard",
    #         "items": {
    #             "std_00_09": (0, 9),
    #             "std_10_19": (10, 19),
    #             "std_20_39": (20, 39),
    #             "std_40_59": (40, 59),
    #             "std_60_79": (60, 79),
    #             "std_80x": (80,)
    #         }
    #     },
    #     "kita_schul": {
    #         "i18n_key": "population.groups.kitaSchul",
    #         "items": {
    #             "ksc_00_02": (0, 2),
    #             "ksc_03_05": (3, 5),
    #             "ksc_06_09": (6, 9),
    #             "ksc_10_14": (10, 14),
    #             "ksc_15_17": (15, 17),
    #             "ksc_18_19": (18, 19),
    #             "ksc_20x": (20,)
    #         }
    #     },
    # }
    populations = {
        "standard": {
            "i18n_key": "population.groups.standard",
            "items": {
                "short_00_09": (0, 17),
                "short_10_19": (18, 29),
                "short_20_29": (30, 49),
                "short_30_39": (50, 64),
                "short_80x": (65,)
            }
        },
        "full": {
            "i18n_key": "population.groups.standard",
            "items": {
                "std_00_09": (0, 9),
                "std_10_19": (10, 19),
                "std_20_29": (20, 29),
                "std_30_39": (30, 39),
                "std_40_49": (40, 49),
                "std_50_59": (50, 59),
                "std_60_69": (60, 69),
                "std_70_79": (70, 79),
                "std_80x": (80,)
            }
        },
    }

    # write populations list
    print("writing population list")
    list_table = get_table("population_list")
    if list_table is None:
        return
    with Session(ENGINE) as session:
        stmt = delete(list_table).where()
        session.execute(stmt)
        for group in populations:
            meta_table_name = f"population_{group}_meta"
            table_name = f"population_{group}"
            stmt = insert(list_table).values(name=group, i18n_key=populations[group]["i18n_key"], meta_table_name=meta_table_name, table_name=table_name)
            session.execute(stmt)
        session.commit()

    # create tables
    print("creating tables")
    for group in populations:
        meta_table_name = f"population_{group}_meta"
        meta_table_spec = [
            Column("pid", Integer, primary_key=True, autoincrement=True),
            Column("age_group_key", String),
            Column("from_", Integer),
            Column("to_", Integer),
        ]
        create_table(meta_table_name, meta_table_spec)
        table_name = f"population_{group}"
        table_spec = [
            Column("pid", Integer, primary_key=True, autoincrement=True),
            Column("geometry", Geometry("POINT", srid=4326)),
            Column("x", Float),
            Column("y", Float),
            Column("utm_x", Float),
            Column("utm_y", Float),
            *[Column(f"{key}", Integer) for key in populations[group]["items"]],
        ]
        create_table(table_name, table_spec)

    #write metatables
    print("writing metatables")
    for group in populations:
        meta_table_name = f"population_{group}_meta"
        meta_table = get_table(meta_table_name)
        if meta_table is None:
            return
        with Session(ENGINE) as session:
            stmt = delete(meta_table).where()
            session.execute(stmt)
            for age_group, sl in populations[group]["items"].items():
                mi = sl[0]
                if len(sl) > 1:
                    ma = sl[1]
                else:
                    ma = -1
                stmt = insert(meta_table).values(age_group_key=age_group, from_=mi, to_=ma)
                session.execute(stmt)
            session.commit()

    # read population data
    print("reading population data")
    population_data = []
    with open(POPULATION_FILE, 'r') as file:
        delimiter = ';'
        header = file.readline()
        tokens = header.split(delimiter)
        indizes = {}
        for i, token in enumerate(tokens):
            indizes[i] = token
        while True:
            line = file.readline()
            if not line:
                break
            tokens = line.split(delimiter)
            attr = {}
            for i, token in enumerate(tokens):
                key = indizes[i]
                if key in ["wgs_x", "wgs_y"]:
                    attr[key] = float(token)
                else:
                    attr[key] = int(token)
            population_data.append(attr)

    # write to tables
    print("writing tables")
    for group in populations:
        print(f"writing group {group}")
        table_name = f"population_{group}"
        pop_table = get_table(table_name)
        if pop_table is None:
            return
        with Session(ENGINE) as session:
            stmt = delete(pop_table).where()
            session.execute(stmt)
            for attr in population_data:
                val = {
                    "geometry": from_shape(Point(attr["wgs_x"], attr["wgs_y"])),
                    "x": attr["wgs_x"],
                    "y": attr["wgs_y"],
                    "utm_x": attr["utm_x"],
                    "utm_y": attr["utm_y"],
                }
                for field in populations[group]["items"]:
                    val[field] = attr[field]
                stmt = insert(pop_table).values(val)
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
            stmt = insert(group_table).values(name=sl[0], i18n_key=sl[1], group_id=sl[2], super_group_id=sl[3])
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
            Column("pid", Integer, primary_key=True, autoincrement=True),
            Column("geometry", Geometry("POINT", srid=4326)),
            Column("weight", Integer),
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
            stmt = insert(list_table).values(name=facility, i18n_key=i18n_key, tooltip_key=tooltip_key, group_id=group_id, table_name=table_name, geometry_column="geometry", weight_column="weight")
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
                        "geometry": from_shape(point),
                        "weight": weight,
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
    insertPopulation()
    print("start inserting Facilities")
    insertFacilityGroups()
    insertFacilities()
