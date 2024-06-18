# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import Table
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.asyncio import AsyncSession

from models import META_DATA

async def create_table(session: AsyncSession, table_name, table_spec):
    if table_name in META_DATA.tables:
        table = META_DATA.tables[table_name]
        await session.execute(table.delete())
        META_DATA.remove(table)
    table = Table(table_name, META_DATA, *table_spec)
    await session.execute(CreateTable(table))
    await session.commit()
    return table

def create_table_sync(session: Session, table_name, table_spec):
    if table_name in META_DATA.tables:
        table = META_DATA.tables[table_name]
        session.execute(table.delete())
        META_DATA.remove(table)
    table = Table(table_name, META_DATA, *table_spec)
    session.execute(CreateTable(table))
    session.commit()
    return table

def get_table(table_name: str) -> Table | None:
    if table_name in META_DATA.tables:
        return META_DATA.tables[table_name]
    return None

async def delete_table(session: AsyncSession, table_name):
    if table_name in META_DATA.tables:
        table = META_DATA.tables[table_name]
        await session.execute(table.delete())
        META_DATA.remove(table)
        await session.commit()

def delete_table_sync(session: Session, table_name):
    if table_name in META_DATA.tables:
        table = META_DATA.tables[table_name]
        session.execute(table.delete())
        META_DATA.remove(table)
        session.commit()
