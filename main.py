# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

import uvicorn.config
import uvicorn.logging

import config
from routers.spatial_access import router as spatial_access_router
from routers.decision_support import router as decision_support_router
from routers.state import router as app_state_router
from routers.data import router as data_router
from services.session import init_state
from services.profile import init_profile_manager
from services.database import init_database
from helpers.log_formatter import ColorFormatter

# create application
app = FastAPI()

# configure cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize services on startup
async def startup_event():
    logging.info("Start loading state...")
    init_state()
    logging.info("Start loading profiles...")
    init_profile_manager()
    logging.info("Start loading database...")
    await init_database()
app.add_event_handler("startup", startup_event)

# add routers to application
app.include_router(spatial_access_router, prefix="/v1/spatial_access")
app.include_router(decision_support_router, prefix="/v1/decision_support")
app.include_router(app_state_router, prefix="/v1/state")
app.include_router(data_router, prefix="/v1/data")

if __name__ == '__main__':
    # configure logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter())
    logger.addHandler(handler)
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(levelprefix)s %(asctime)s - %(client_addr)s - \"%(request_line)s\" %(status_code)s"
    log_config["formatters"]["default"]["fmt"] = "%(levelprefix)s %(asctime)s - %(message)s"

    # start application
    uvicorn.run("main:app", host=config.API_HOST, port=config.API_PORT, log_config=log_config)
