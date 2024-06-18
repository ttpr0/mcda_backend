# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

META_DATA: MetaData = MetaData()

Base = declarative_base(metadata=META_DATA)

# from .users import User
# from .planning_areas import PlanningArea
# from .physicians import PhysiciansCountBased, PhysiciansLocationBased, PhysiciansList, SupplyLevelList
# from .population import Population
# from .facilities import Facility

del Base
