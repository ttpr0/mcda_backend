# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

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
