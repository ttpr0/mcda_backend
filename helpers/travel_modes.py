# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

DEFAULT_TRAVEL_MODE = "driving-car"
TRAVEL_MODES = {
    "driving-car": {
        "text": "PKW",
        "valid": True
    },
    "walking-foot": {
        "text": "Fuß",
        "valid": False
    },
    "public-transit": {
        "text": "ÖPNV",
        "valid": False
    },
}

def get_default_travel_mode() -> str:
    return DEFAULT_TRAVEL_MODE

def is_valid_travel_mode(travel_mode: str) -> bool:
    if travel_mode not in TRAVEL_MODES:
        return False
    item = TRAVEL_MODES[travel_mode]
    if item["valid"] is False:
        return False
    return True

def get_distance_decay(travel_mode: str, decay_type: str, supply_level: str, facility_type: str) -> tuple[list[float], list[float]]:
    if decay_type == 'linear':
        if supply_level == "generalPhysician":
            ranges = [120., 240., 360., 480., 600., 720., 840., 960., 1080., 1200.]
            factors = [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            return (ranges, factors)
        elif supply_level == "generalSpecialist" and facility_type != "Kinderärzte":
            ranges = [240., 480., 720., 960., 1200., 1440., 1680., 1920., 2160., 2400.]
            factors = [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            return (ranges, factors)
        elif supply_level == "generalSpecialist":
            ranges = [180., 360., 540., 720., 900., 1080., 1260., 1440., 1620., 1800.]
            factors = [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            return (ranges, factors)
        else:
            ranges = [360., 720., 1080., 1440., 1800., 2160., 2520., 2880., 3240., 3600.]
            factors = [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
            return (ranges, factors)
    if decay_type == 'patient_behavior':
        ranges = [230., 345., 495., 590., 725., 800., 890., 945., 995., 1080., 1140.]
        factors = [1., 0.603, 0.345, 0.251, 0.183, 0.135, 0.103, 0.084, 0.059, 0.046, 0.031]
        return (ranges, factors)
    
    if decay_type == 'minimum_standards':
        ranges = [100., 200., 300., 400., 500., 600., 700., 800., 900.]
        factors = [1., 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
        return (ranges, factors)
    
    return ([], [])
