# Models

This package contains functions to aquire data and to make requests to the DB.

Generally data is stored in the PostGIS-DB and function will make requests to that DB to get the relevant information. Direct requests to the DB through the underlying SQLAlchemy connection are usually not neccessary.

Population data is (for performance reasons) not stored in the DB thus before starting the server information will be loaded from the given population-file (*./population.py* *load_population* function). For format of the population-file please consult *files/doc.md*.

## Table Specification

Tables are created and managed directly through SQLAlchemy-Core (ORM is not used, see *./util.py*).

For table-specifications (columns, ...) see *./tables.py*.

## Table Creation

Tables are created on package-loading if they dont already exist (see *./__init__.py*).

Because most functions of the MCDA-Backend depend on the data provided by the DB, tables should already be created and population before running the server (see *../doc.md* for more information).
