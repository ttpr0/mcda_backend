# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

DEFAULT_TRAVEL_MODE = "driving-car"
TRAVEL_MODES = {
    "driving-car": {
        "text": "travelModes.pkw",
        "valid": True
    },
    "walking-foot": {
        "text": "travelModes.fuss",
        "valid": False
    },
    "public-transit": {
        "text": "travelModes.opnv",
        "valid": False
    },
}

def get_default_travel_mode() -> str:
    return DEFAULT_TRAVEL_MODE

def get_available_travelmodes():
    return TRAVEL_MODES

def is_valid_travel_mode(travel_mode: str) -> bool:
    if travel_mode not in TRAVEL_MODES:
        return False
    item = TRAVEL_MODES[travel_mode]
    if item["valid"] is False:
        return False
    return True

DISTANCE_DECAYS = {
    "linear": {
        "text": "distanceDecays.linear"
    },
    "patient_behavior": {
        "text": "distanceDecays.patientBehavior"
    },
    "minimum_standards": {
        "text": "distanceDecays.minimumStandards"
    }
}

def get_available_decays():
    return DISTANCE_DECAYS

def get_distance_decay(travel_mode: str, decay_type: str, supply_level: str, facility_type: str) -> tuple[list[float], list[float]]:
    """Returns distance decay for parameters as (ranges, factors) tuple
    """
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
