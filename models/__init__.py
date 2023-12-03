# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import create_engine, Engine, MetaData
from sqlalchemy.event import listen
from sqlalchemy.orm import declarative_base
from geoalchemy2 import load_spatialite

import config

ENGINE: Engine = create_engine(f"postgresql+psycopg2://{config.POSTGIS_USER}:{config.POSTGIS_PASSWORD}@{config.POSTGIS_HOST}:5432/{config.POSTGIS_DB}")
# ENGINE: Engine = create_engine("sqlite:///./files/gis.db")
# listen(ENGINE, "connect", load_spatialite)

META_DATA: MetaData = MetaData()
META_DATA.reflect(bind=ENGINE)

from .util import create_table, get_table, delete_table

# Base = declarative_base()

# from .users import User
# from .planning_areas import PlanningArea
# from .physicians import PhysiciansCountBased, PhysiciansLocationBased, PhysiciansList, SupplyLevelList
# from .population import Population
# from .facilities import Facility

# Base.metadata.create_all(ENGINE)

# del Base

from .tables import TABLE_SPECS

for spec in TABLE_SPECS:
    if get_table(spec["name"]) is None:
        create_table(spec["name"], spec["columns"])
