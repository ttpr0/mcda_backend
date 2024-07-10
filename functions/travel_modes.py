# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

"""Utility functions for available traval-modes and distance decays
"""

TRAVEL_MODES = ["driving-car", "walking-foot", "public-transit"]

def is_valid_travel_mode(travel_mode: str) -> bool:
    if travel_mode not in TRAVEL_MODES:
        return False
    return True

def get_default_travel_mode() -> str:
    return "driving-car"

def get_distance_decay(travel_mode: str, decay_type: str, supply_level: str, facility_type: str) -> dict:
    """Returns distance decay for parameters as (ranges, factors) tuple
    """
    if decay_type == 'linear':
        if supply_level == "generalPhysician":
            return {
                "decay_type": "hybrid",
                "ranges": [120., 240., 360., 480., 600., 720., 840., 960., 1080., 1200.],
                "range_factors": [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            }
        elif supply_level == "generalSpecialist" and facility_type != "paediatrician":
            return {
                "decay_type": "hybrid",
                "ranges": [240., 480., 720., 960., 1200., 1440., 1680., 1920., 2160., 2400.],
                "range_factors": [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            }
        elif supply_level == "generalSpecialist":
            return {
                "decay_type": "hybrid",
                "ranges": [180., 360., 540., 720., 900., 1080., 1260., 1440., 1620., 1800.],
                "range_factors": [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            }
        else:
            return {
                "decay_type": "hybrid",
                "ranges": [360., 720., 1080., 1440., 1800., 2160., 2520., 2880., 3240., 3600.],
                "range_factors": [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            }
    if decay_type == 'patient_behavior':
        return {
            "decay_type": "hybrid",
            "ranges": [230., 345., 495., 590., 725., 800., 890., 945., 995., 1080., 1140.],
            "range_factors": [1., 0.603, 0.345, 0.251, 0.183, 0.135, 0.103, 0.084, 0.059, 0.046, 0.031]
        }
    if decay_type == 'minimum_standards':
        return {
            "decay_type": "hybrid",
            "ranges": [100., 200., 300., 400., 500., 600., 700., 800., 900.],
            "range_factors": [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
        }
    
    return {}

TIME_ZONES = {
    "supermarket": (2, 5, 10, 20),
    "discounter": (2, 5, 10, 20),
    "other_local_supply": (2, 5, 10, 20),
    "pharmacy": (2, 4, 8, 15),
    "clinic": (3, 7, 15, 30),
    "physicians": (3, 7, 13, 25),
    "nursery": (2, 7, 15, 30),
    "primary_school": (2, 5, 23, 45),
    "secondary_school_1": (2, 15, 30, 60),
    "secondary_school_2": (2, 15, 30, 60),
}

def get_default_timezones(facilities: list[str]) -> dict[str, tuple[int]]:
    zones = {}
    for f in facilities:
        if f in TIME_ZONES:
            zones[f] = TIME_ZONES[f]
        else:
            zones[f] = (2, 5, 10, 20)
    return zones
