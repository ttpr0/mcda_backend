# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from typing import Any, Callable
import json
import requests
import numpy as np

import config


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
