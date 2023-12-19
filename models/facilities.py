# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from sqlalchemy import select
from geoalchemy2.shape import from_shape
from sqlalchemy.orm import Session
from shapely import Point, Polygon

from . import ENGINE, get_table

def get_facility(name: str, envelop: Polygon) -> tuple[list[tuple[float, float]], list[float]]:
    locations = []
    weights = []
    with Session(ENGINE) as session:
        facility_table = get_table("facilities")
        if facility_table is None:
            return (locations, weights)
        stmt = select(facility_table.c.wgs_x, facility_table.c.wgs_y, facility_table.c.weight).where((facility_table.c.group==name) & facility_table.c.point.ST_Within(envelop.wkt))
        rows = session.execute(stmt).fetchall()
        for row in rows:
            wgs_x: float = row[0]
            wgs_y: float = row[1]
            weight: float = row[2]
            locations.append((wgs_x, wgs_y))
            weights.append(weight)
    return locations, weights

FACILITIES = {
    "localSupply": {
        "text": "localSupply.text",
        "items": {
            "supermarket": {"text": "localSupply.supermarket"},
            "discounter": {"text": "localSupply.discounter"},
            "other_local_supply": {"text": "localSupply.otherLocalSupply", "tooltip": "tooltip.otherLocalSupply"}
        }
    },
    "health": {
        "text": "health.text",
        "items": {
            "pharmacy": {"text": "health.pharmacy"},
            "clinic": {"text": "health.clinic"},
            "physicians": {"text": "health.physicians.text", "items": {
                "general_physician": {"text": "health.physicians.generalPhysicians"},
                "paediatrician": {"text": "health.physicians.paediatrician"},
                "ophthalmologist": {"text": "health.physicians.ophthalmologist"},
                "surgeon": {"text": "health.physicians.surgeon"},
                "gynaecologist": {"text": "health.physicians.gynaecologist"},
                "dermatologist": {"text": "health.physicians.dermatologist"},
                "otolaryngologist": {"text": "health.physicians.otolaryngologist"},
                "neurologist": {"text": "health.physicians.neurologist"},
                "psychotherapist": {"text": "health.physicians.psychotherapists"},
                "urologist": {"text": "health.physicians.urologists"}
            }
            }
        }
    },
    "education": {
        "text": "education.text",
        "items": {
            "nursery": {"text": "education.nursery", "tooltip": "tooltip.nursery"},
            "primary_school": {"text": "education.primarySchool", "tooltip": "tooltip.primarySchool"},
            "secondary_school_1": {"text": "education.secondarySchool1", "tooltip": "tooltip.secondarySchool1"},
            "secondary_school_2": {"text": "education.secondarySchool2", "tooltip": "tooltip.secondarySchool2"}
        }
    }
}

def get_available_facilities():
    return FACILITIES
