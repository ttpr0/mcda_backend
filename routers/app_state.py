# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from fastapi import APIRouter
from pydantic import BaseModel
import requests
import json
import asyncio
import time
import os


router = APIRouter()

@router.get("/facilities")
async def get_available_facilities():
    return {
        "Nahversorgung": [
            {"name": "supermarket", "text": "Supermärkte"},
            {"name": "discounter", "text": "Discounter"},
            {"name": "other_local_supply", "text": "sonstige Lebensmittelgeschäfte"}
        ],
        "Gesundheit": [
            {"name": "pharmacy", "text": "Apotheken"},
            {"name": "clinic", "text": "Hochschulkliniken und Plankrankenhäuser"},
            {"name": "paediatrician", "text": "Kinder- und Jugendärzte"},
            {"name": "ophthalmologist", "text": "Augenärzte"},
            {"name": "surgeon", "text": "Chirurgen und Orthopäden"},
            {"name": "gynaecologist", "text": "Frauenärzte"},
            {"name": "dermatologist", "text": "Hautärzte"}
        ],
        "Bildung": [
            {"name": "nursery", "text": "Kindertagesstätten"},
            {"name": "primary_school", "text": "Primärschulen"},
            {"name": "secondary_school_1", "text": "Sekundarstufe Bereich 1, ohne (Fach)Hochschulreife"},
            {"name": "secondary_school_2", "text": "Sekundarstufe Bereich 1 und 2, mit Möglichkeit zu Erwerb der (Fach)Hochschulreife"}
        ]
    }


class AvailableAttributesRequest(BaseModel):
    facility_type: str

@router.post("/facility_attributes")
async def get_available_attribs(req: AvailableAttributesRequest):
    return {
        "attributes": [
            ("name", "string"),
            ("value", "float"),
            ("count", "int")
        ]
    }