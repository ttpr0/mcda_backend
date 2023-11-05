# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import asyncio

import config
from models.population import load_population
from routers.nearest_query import router as nearest_router
from routers.spatial_access import router as spatial_access_router
from routers.spatial_analysis import router as spatial_analysis_router
from routers.login import router as login_router
from routers.app_state import router as app_state_router
from routers.others import router as others_router
from routers.decision_support import router as decision_support_router
from state import USER_SESSIONS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.middleware("http")
# async def check_session_key(request: Request, call_next):
#     if request.url.path == "/v1/util/login":
#         response = await call_next(request)
#         return response
#     if "Session-Key" not in request.headers:
#         return JSONResponse(content={
#             "error": "missing session_key header"
#         }, status_code=401)
#     key = request.headers["Session-Key"]
#     if key not in USER_SESSIONS:
#         return JSONResponse(content={
#             "error": "invalid session_key header"
#         }, status_code=401)
#     response = await call_next(request)
#     return response


app.include_router(nearest_router, prefix="/v1/accessibility/nearest_query")

app.include_router(spatial_access_router, prefix="/v1/spatial_access")

app.include_router(decision_support_router, prefix="/v1/decision_support")

app.include_router(spatial_analysis_router, prefix="/v1/spatial_analysis")

app.include_router(login_router, prefix="/v1/util")

app.include_router(app_state_router, prefix="/v1/state")

app.include_router(others_router, prefix="/v1")


class ColorFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[90m"
    green = "\x1b[92m"
    yellow = "\x1b[93m"
    red = "\x1b[91m"
    reset = "\x1b[0m"

    COLORS = {
        logging.DEBUG: grey,
        logging.INFO: green,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: red
    }

    def format(self, record):
        record.levelname = 'WARN' if record.levelname == 'WARNING' else record.levelname
        record.levelname = 'ERROR' if record.levelname == 'CRITICAL' else record.levelname
        log_clr = self.COLORS[record.levelno]
        formatter = logging.Formatter(
            f"{log_clr}%(levelname)s{self.reset}: %(asctime)s -> %(message)s")
        return formatter.format(record)


if __name__ == '__main__':
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    # handler.setFormatter(logging.Formatter("%(levelname)s - %(asctime)s - %(message)s"))
    handler.setFormatter(ColorFormatter())
    logger.addHandler(handler)

    logger.info("Start loading population data...")
    load_population(config.POPULATION_FILE)
    logger.info("Done loading population data.")
    logger.info("AccessibilityService ready!")
    # uvicorn.run("main:app", host=config.API_HOST, port=config.API_PORT, reload=True)
    uvicorn.run("main:app", host=config.API_HOST, port=config.API_PORT)
