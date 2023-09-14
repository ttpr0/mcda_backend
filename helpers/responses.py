# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from typing import Any, Callable
import json
import requests
import numpy as np

import config

# from helpers.geoserver_api import add_featurestore, open_conncection
# from helpers.postgis_api import add_results


class GridFeature:
    def __init__(self, x: float, y: float, value):
        self.x: float = x
        self.y: float = y
        self.value = value

class GridResponse:
    crs: str
    extend: list[float]
    size: list[int]
    features: list[GridFeature]

    def __init__(self, features, crs, extend, size):
        self.features = features
        self.extend = extend
        self.size = size
        self.crs = crs


def build_remote_grid(features: list, extent: tuple[float, float, float, float]) -> int:
    """
    Creates remote-grid layer and returns layer id.
    """
    header = {"Content-Type": "application/json"}
    body = {
        "features": features,
        "extent": extent,
    }
    data = json.dumps(body)
    resp = requests.post("http://localhost:5004/v0/create_grid", data=data, headers=header)

    layer_id = resp.json()["id"]
    return layer_id


def build_geoserver_grid(features: list, extent: tuple[float, float, float, float]) -> str:
    """
    Creates layer on geoserver and returns wms-layer name.
    """
    # features = []
    # for i, p in enumerate(points):
    #     if not filt(i):
    #         continue
    #     access: float = float(values[i])
    #     features.append((access, p[0], p[1]))

    # # test geosever
    # add_results(features)

    # geo = open_conncection(config.GEOSERVER_URL, 'admin', 'geoserver')
    # add_featurestore(geo, "access_data", "demo", "access")

    return "access"