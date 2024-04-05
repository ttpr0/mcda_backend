# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import Column, Integer, String, Float, ARRAY, Boolean
from geoalchemy2 import Geometry


USER_TABLE_SPEC = {
    "name": "users",
    "columns": [
        Column("PID", Integer, primary_key=True, autoincrement=True),
        Column("EMAIL", String(50)),
        Column("PASSWORD_SALT", String(20)),
        Column("PASSWORD_HASH", String),
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

FACILITY_GROUPS_TABLE_SPEC = {
    "name": "facilities_groups",
    "columns": [
        Column("PID", Integer, primary_key=True, autoincrement=True),
        Column("NAME", String(50)),
        Column("I18N_KEY", String(50)),
        Column("GROUP_ID", Integer, unique=True),
        Column("UNIQUE", Boolean, default=False),
        Column("SUPER_GROUP_ID", Integer, nullable=True, default=None),
    ]
}

FACILITY_LIST_TABLE_SPEC = {
    "name": "facilities_list",
    "columns": [
        Column("PID", Integer, primary_key=True, autoincrement=True),
        Column("NAME", String(50)),
        Column("I18N_KEY", String(50)),
        Column("TOOLTIP_KEY", String(50), nullable=True),
        Column("GROUP_ID", Integer),
        Column("TABLE_NAME", String),
        Column("GEOMETRY_COLUMN", String),
        Column("WEIGHT_COLUMN", String),
    ]
}

SUPPLY_LEVEL_TABLE_SPEC = {
    "name": "supply_level_list",
    "columns": [
        Column("PID", Integer, primary_key=True, autoincrement=True),
        Column("NAME", String(50)),
        Column("I18N_KEY", String(50)),
        Column("VALID", Boolean),
        Column("SUPPLY_LEVEL_ID", Integer, unique=True),
    ]
}

PLANNING_AREA_TABLE_SPEC = {
    "name": "planning_areas",
    "columns": [
        Column("PID", Integer, primary_key=True, autoincrement=True),
        Column("NAME", String(50)),
        Column("I18N_KEY", String(50)),
        Column("SUPPLY_LEVEL_IDS", ARRAY(Integer)),
        Column("GEOMETRY", Geometry('POLYGON', srid=4326)),
    ]
}

PHYSICIANS_LIST_TABLE_SPEC = {
    "name": "physicians_list",
    "columns": [
        Column("PID", Integer, primary_key=True, autoincrement=True),
        Column("NAME", String(50)),
        Column("I18N_KEY", String(50)),
        Column("SUPPLY_LEVEL_IDS", ARRAY(Integer)),
        Column("PHYSICIAN_ID", Integer, unique=True),
    ]
}

PHYSICIANS_LOCATION_TABLE_SPEC = {
    "name": "physicians_locations",
    "columns": [
        Column("PID", Integer, primary_key=True, autoincrement=True),
        Column("GEOMETRY", Geometry('POINT', srid=4326), index=True),
        Column("PHYSICIAN_ID", Integer),
        Column("VBE_VOLUME", Float),
        Column("PHYSICIAN_COUNT", Float),
    ]
}

TABLE_SPECS = [
    USER_TABLE_SPEC, POPULATION_TABLE_SPEC, FACILITY_GROUPS_TABLE_SPEC, FACILITY_LIST_TABLE_SPEC, PLANNING_AREA_TABLE_SPEC, SUPPLY_LEVEL_TABLE_SPEC,
    PHYSICIANS_LIST_TABLE_SPEC, PHYSICIANS_LOCATION_TABLE_SPEC
]
