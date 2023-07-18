# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

from .users import User
from .planning_areas import PlanningArea
from .physicians import PhysiciansCountBased, PhysiciansLocationBased, PhysiciansList, SupplyLevelList
from .population import Population
from .facilities import Facility

import config

engine = create_engine(f"postgresql+psycopg2://{config.POSTGIS_USER}:{config.POSTGIS_PASSWORD}@{config.POSTGIS_HOST}:5432/{config.POSTGIS_DB}")
Base.metadata.create_all(engine)

del Base