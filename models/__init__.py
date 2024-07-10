# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""Creates the tables in the database.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

META_DATA: MetaData = MetaData()

Base = declarative_base(metadata=META_DATA)

# orm tables should be imported hear, e.g.
# from .users import User

del Base
