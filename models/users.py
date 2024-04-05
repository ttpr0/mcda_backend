# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import create_engine, Column, Integer, String
from geoalchemy2 import Geometry
from sqlalchemy.orm import Session, declarative_base
from shapely import Point, Polygon

from . import ENGINE, get_table
