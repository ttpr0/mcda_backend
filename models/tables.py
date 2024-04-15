# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import Column, Integer, String, Float, ARRAY, Boolean
from geoalchemy2 import Geometry


USER_TABLE_SPEC = {
    "name": "users",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("username", String(50), unique=True),
        Column("email", String(50)),
        Column("group", String(10)),
        Column("password_salt", String(20)),
        Column("password_hash", String),
    ]
}

POPULATION_LIST_TABLE_SPEC = {
    "name": "population_list",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("name", String(50)),
        Column("i18n_key", String(50)),
        Column("table_name", String),
        Column("meta_table_name", String),
    ]
}

FACILITY_GROUPS_TABLE_SPEC = {
    "name": "facilities_groups",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("name", String(50)),
        Column("i18n_key", String(50)),
        Column("group_id", Integer, unique=True),
        Column("unique", Boolean, default=False),
        Column("super_group_id", Integer, nullable=True, default=None),
    ]
}

FACILITY_LIST_TABLE_SPEC = {
    "name": "facilities_list",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("name", String(50)),
        Column("i18n_key", String(50)),
        Column("tooltip_key", String(50), nullable=True),
        Column("group_id", Integer),
        Column("table_name", String),
        Column("geometry_column", String),
        Column("weight_column", String),
    ]
}

SUPPLY_LEVEL_TABLE_SPEC = {
    "name": "supply_level_list",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("name", String(50)),
        Column("i18n_key", String(50)),
        Column("valid", Boolean),
        Column("supply_level_id", Integer, unique=True),
    ]
}

PLANNING_AREA_TABLE_SPEC = {
    "name": "planning_areas",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("name", String(50)),
        Column("i18n_key", String(50)),
        Column("supply_level_ids", ARRAY(Integer)),
        Column("geometry", Geometry('POLYGON', srid=4326)),
    ]
}

PHYSICIANS_LIST_TABLE_SPEC = {
    "name": "physicians_list",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("name", String(50)),
        Column("i18n_key", String(50)),
        Column("supply_level_ids", ARRAY(Integer)),
        Column("physician_id", Integer, unique=True),
    ]
}

PHYSICIANS_LOCATION_TABLE_SPEC = {
    "name": "physicians_locations",
    "columns": [
        Column("pid", Integer, primary_key=True, autoincrement=True),
        Column("geometry", Geometry('POINT', srid=4326), index=True),
        Column("physician_id", Integer),
        Column("vbe_volume", Float),
        Column("physician_count", Float),
    ]
}

TABLE_SPECS = [
    USER_TABLE_SPEC, POPULATION_LIST_TABLE_SPEC, FACILITY_GROUPS_TABLE_SPEC, FACILITY_LIST_TABLE_SPEC, PLANNING_AREA_TABLE_SPEC, SUPPLY_LEVEL_TABLE_SPEC,
    PHYSICIANS_LIST_TABLE_SPEC, PHYSICIANS_LOCATION_TABLE_SPEC
]
