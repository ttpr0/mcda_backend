# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from shapely import Polygon
from shapely.ops import transform
from pyproj import Transformer

from .dummy_decay import get_max_distance

def get_extent(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    minx = 1000000000
    maxx = -1
    miny = 1000000000
    maxy = -1
    for i, p in enumerate(points):
        if p[0] < minx:
            minx = p[0]
        if p[0] > maxx:
            maxx = p[0]
        if p[1] < miny:
            miny = p[1]
        if p[1] > maxy:
            maxy = p[1]
    return minx, miny, maxx, maxy

def get_query_from_extent(envelop: tuple[float, float, float, float]) -> Polygon:
    ll = (envelop[0], envelop[1])
    ur = (envelop[2], envelop[3])
    query = Polygon(((ll[0], ll[1]), (ll[0], ur[1]), (ur[0], ur[1]), (ur[0], ll[1])))
    return query

def get_buffered_query(query: Polygon, travel_mode: str, decay: dict) -> Polygon:
    project = Transformer.from_crs("epsg:4326", "epsg:25832", always_xy=True).transform
    utm_query: Polygon = transform(project, query)
    time = get_max_distance(decay)
    match travel_mode:
        case "driving-car":
            speed = 60
        case "cycling-bike":
            speed = 10
        case "walking-foot":
            speed = 4
        case "public-transit":
            speed = 30
    utm_query_buffer = utm_query.buffer(time * speed / 3.6)
    project = Transformer.from_crs("epsg:25832", "epsg:4326", always_xy=True).transform
    query_buffer: Polygon = transform(project, utm_query_buffer)
    return query_buffer

def deprecated(func):
    def wrapped(*args, **kwargs):
        print(f"DeprecationWarning: Outdated function \"{func.__name__}\" called. Consider updating your code.")
        return func(*args, **kwargs)
    return wrapped
