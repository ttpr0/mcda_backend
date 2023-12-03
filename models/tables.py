# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import Column, Integer, String, Float
from geoalchemy2 import Geometry


USER_TABLE_SPEC = {
    "name": "users",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("email", String(50)),
        Column("password_salt", String(20)),
        Column("password_hash", String),
    ]
}

POPULATION_TABLE_SPEC = {
    "name": "population",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("point", Geometry('POINT'), index=True),
        Column("wgs_x", Float),
        Column("wgs_y", Float),
        Column("utm_x", Float),
        Column("utm_y", Float),

        Column("ew_gesamt", Integer),
        Column("std_00_09", Integer),
        Column("std_10_19", Integer),
        Column("std_20_39", Integer),
        Column("std_40_59", Integer),
        Column("std_60_79", Integer),
        Column("std_80x", Integer),
        Column("ksc_00_02", Integer),
        Column("ksc_03_05", Integer),
        Column("ksc_06_09", Integer),
        Column("ksc_10_14", Integer),
        Column("ksc_15_17", Integer),
        Column("ksc_18_19", Integer),
        Column("ksc_20x", Integer),
    ]
}

FACILITY_TABLE_SPEC = {
    "name": "facilities",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("group", String),
        Column("point", Geometry('POINT'), index=True),
        Column("wgs_x", Float),
        Column("wgs_y", Float),
        Column("weight", Float),
    ]
}

PLANNING_AREA_TABLE_SPEC = {
    "name": "planning_areas",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("name", String(50)),
        Column("geom", Geometry('POLYGON')),
    ]
}

SUPPLY_LEVEL_TABLE_SPEC = {
    "name": "supply_level_list",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("name", String(50)),
        Column("TYP_ID", Integer),
    ]
}

PHYSICIANS_LIST_TABLE_SPEC = {
    "name": "physicians_list",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("name", String(50)),
        Column("TYP_ID", Integer),
        Column("DETAIL_ID", Integer),
    ]
}

PHYSICIANS_LOCATION_BASED_TABLE_SPEC = {
    "name": "physicians_location_based",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("point", Geometry('POINT')),
        Column("TYP_ID", Integer),
        Column("DETAIL_ID", Integer),
        Column("count", Integer),
    ]
}

PHYSICIANS_COUNT_BASED_TABLE_SPEC = {
    "name": "physicians_count_based",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("point", Geometry('POINT')),
        Column("TYP_ID", Integer),
        Column("DETAIL_ID", Integer),
        Column("VBE_Sum", Float),
        Column("Pys_Count", Float),
    ]
}

TABLE_SPECS = [
    USER_TABLE_SPEC, POPULATION_TABLE_SPEC, FACILITY_TABLE_SPEC, PLANNING_AREA_TABLE_SPEC, SUPPLY_LEVEL_TABLE_SPEC,
    PHYSICIANS_LIST_TABLE_SPEC, PHYSICIANS_LOCATION_BASED_TABLE_SPEC, PHYSICIANS_COUNT_BASED_TABLE_SPEC
]
