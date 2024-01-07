# Documentation of the MCDA-Backend Repository

## Running the server

To run the MCDA-Backend use *docker* and the provided *docker-compose.yml* file.

Else simply install dependencies from *requirements.txt* and run *main.py*.

## Expected dependencies

* a PostgreSQL/PostGIS-Database containing all necessary tables (see ./models/tables.py for table definition)
* to populate the DB from the data inside the ./files folder run the *populate.py* script (for documentation of the expected layout and content see ./files/doc.md)
* to create the neccessary files for the ./files folder run the script *extract_poi.py* (it will extract neccessary POI from a OSM-POI file and write them to ./files).

* a valid DVAN-Population-File (might change in future) containing population age-groups and counts

## Configuration

Configuration happens through the *config.py* file.

Parameters are:

* ACCESSIBILITY_URL: url-prefix of a running OpenAccessibility-Server (github.com/ttpr0/openaccessibilityservice)

* POSTGIS_HOST: IP-address of the DB (expected to listen on default port 5432)
* POSTGIS_USER/POSTGIS_PASSWORD/POSTGIS_DB: user, password and db used to access data on DB-Server

* API_HOST/API_PORT: host and port this server will listen on (should match *docker-compose.yml* configuration)

* POPULATION_FILE: path to DVAN-population-File to be used

## Project structure

(note that all subfolders contain seperate *doc.md* for further information)

* ./files: contains static resources (e.g. the population-file)
* ./helpers: useful helpers without association to one of the other packages
* ./models: central DB access points are defined here; contains routines to fetch relevant information from the datastores (e.g. "get population in extent", "get available travel modes", ...)
* ./oas_api: wrapper function for requests to the OpenAccessibilityService
* ./routers: API-Routers to handle Front-End requests; routers are registered in *main.py* (consult *main.py* for information on query-path prefixes of different routers)
