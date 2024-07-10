# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""Service for interacting with the database.
"""

from typing import AsyncGenerator, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session

import config
from models import META_DATA
from models.tables import TABLE_SPECS
from functions.util import get_table, create_table

ENGINE = None
SESSION_MAKER = None

async def init_database():
    """Initializes the database connection and creates the tables if they don't exist.
    """
    global ENGINE
    ENGINE = create_async_engine(f"postgresql+asyncpg://{config.POSTGIS_USER}:{config.POSTGIS_PASSWORD}@{config.POSTGIS_HOST}:5432/{config.POSTGIS_DB}")
    global SESSION_MAKER
    SESSION_MAKER = async_sessionmaker(bind=ENGINE, expire_on_commit=False)
    async with ENGINE.connect() as conn:
        await conn.run_sync(META_DATA.reflect)
        await conn.run_sync(META_DATA.create_all)
    async with AsyncSession(ENGINE) as session:
        for spec in TABLE_SPECS:
            if get_table(spec["name"]) is None:
                await create_table(session, spec["name"], spec["columns"])

async def get_db_session() -> AsyncGenerator[AsyncSession, Any]:
    """Creates a database session.
    
    Note:
        - this function should be used as a fastapi dependency
    """
    global SESSION_MAKER
    if SESSION_MAKER is None:
        raise ValueError("This should not have happened.")
    db = SESSION_MAKER()
    try:
        yield db
    finally:
        await db.close()
