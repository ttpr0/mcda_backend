# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import Table

from . import ENGINE, META_DATA


def create_table(table_name, table_spec):
    with ENGINE.connect() as conn:
        if table_name in META_DATA.tables:
            table = META_DATA.tables[table_name]
            table.drop(bind=ENGINE)
            conn.commit()
            META_DATA.remove(table)

        table = Table(table_name, META_DATA, *table_spec)
        table.create(bind=ENGINE)
        conn.commit()

    return table


def get_table(table_name: str) -> Table | None:
    if table_name in META_DATA.tables:
        return META_DATA.tables[table_name]
    return None

def delete_table(table_name):
    with ENGINE.connect() as conn:
        if table_name in META_DATA.tables:
            table = META_DATA.tables[table_name]
            table.drop(bind=ENGINE)
            conn.commit()
            META_DATA.remove(table)
