# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import json
from shapely import contains_xy, Polygon
import sqlite3
import random

def read(db, table) -> list[tuple]:
    conn = None
    try:
        conn = sqlite3.connect(db)
    except Exception as e:
        print(e)
        return []

    cur = conn.cursor()

    # sql_query = """
    # SELECT name FROM sqlite_master  
    # WHERE type='table';
    # """
    sql_query = f"""
    SELECT * FROM {table};
    """
    cur.execute(sql_query)
    rows = cur.fetchall()

    data = []
    for row in rows:
        data.append(row)
    
    return data

def join_category_points(locs, categories):
    cat_dict = {}
    for id, cat in categories:
        cat_dict[id] = cat

    joined = []
    for id, lat, lon in locs:
        joined.append((lon, lat, cat_dict[id]))

    return joined

def read_filter_polygon(filename):
    with open(filename, "r") as file:
        data = json.loads(file.read())
        geom = data["features"][0]["geometry"]
        typ = geom["type"]
        coordinates = geom["coordinates"]
        return Polygon(coordinates[0])

CATEGORY_MAPPING = {
    296: "supermarket",
    225: "other_local_supply",
    229: "other_local_supply",
    233: "other_local_supply",
    262: "other_local_supply",
    265: "other_local_supply",
    274: "other_local_supply",
    35: "clinic",
    34: "pharmacy",
    38: "physician",
    11: "nursery",
    12: "school",
}

SPLIT_CATEGORIES = {
    "supermarket": {
        "indices": (0, 0, 1, 1, 1),
        "categories": ("supermarket", "discounter") 
    },
    "school": {
        "indices": (0, 1, 2),
        "categories": ("primary_school", "secondary_school_1", "secondary_school_2") 
    },
    "physician": {
        "indices": (0, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9),
        "categories": ("dermatologist", "general_physician", "gynaecologist", "neurologist", "ophthalmologist", "otolaryngologist", "paediatrician", "psychotherapist", "surgeon", "urologist") 
    },
}

def _select_random_category(categories, indices):
    return categories[random.choice(indices)]

def extract_locations(poi, filter_polygon):
    global CATEGORY_MAPPING, SPLIT_CATEGORIES
    locs = {}
    for lon, lat, cat_id in poi:
        if cat_id not in CATEGORY_MAPPING:
            continue
        if not contains_xy(filter_polygon, lon, lat):
            continue
        cat = CATEGORY_MAPPING[cat_id]
        if cat in SPLIT_CATEGORIES:
            cat_data = SPLIT_CATEGORIES[cat]
            cat = _select_random_category(cat_data["categories"], cat_data["indices"])
        if cat not in locs:
            locs[cat] = []
        locs[cat].append((lon, lat))
    return locs

def write_facilities(locs_dict):
    for cat in locs_dict:
        with open(f"./files/facilities/{cat}.geojson", "w") as file:
            features = []
            for lon, lat in locs_dict[cat]:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "Weight": random.randint(1, 100)
                    }
                })
            data = {
                "type": "FeatureCollection",
                "features": features
            }
            file.write(json.dumps(data))

PHYSICIAN_IDS = {
    "general_physician": (100, 100),
    "ophthalmologist": (200, 205),
    "surgeon": (200, 212),
    "gynaecologist": (200, 235),
    "dermatologist": (200, 225),
    "otolaryngologist": (200, 220),
    "paediatrician": (200, 245),
    "neurologist": (200, 230),
    "psychotherapist": (200, 250),
    "urologist": (200, 240),
    "internisten": (300, 302),
    "jugendpsychiater": (300, 303),
    "radiologen": (300, 304),
    "anasthesisten": (300, 301)
}

def write_physicians(locs_dict):
    spec_count_features = []
    loc_features = []
    for cat in locs_dict:
        if cat not in PHYSICIAN_IDS:
            continue
        typ_id, detail_id = PHYSICIAN_IDS[cat]
        for lon, lat in locs_dict[cat]:
            spec_count_features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "TYP_ID": typ_id,
                    "DETAIL_ID_1": detail_id,
                    "VBE_Sum": random.randint(1, 10),
                    "Pys_count": random.randint(1, 10),
                }
            })
            loc_features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "TYP_ID": typ_id,
                    "DETAIL_ID_1": detail_id,
                }
            })
    spec_count_data = {
        "type": "FeatureCollection",
        "features": spec_count_features
    }
    loc_data = {
        "type": "FeatureCollection",
        "features": loc_features
    }
    with open("./files/physicians/outpatient_physician_location_specialist_count.geojson", "w") as file:
        file.write(json.dumps(spec_count_data))
    with open("./files/physicians/outpatient_physician_location_based.geojson", "w") as file:
        file.write(json.dumps(loc_data))

def write_categories(data):
    with open("poi_category_map.csv", "w") as file:
        file.write("ID;Category\n")
        for row in data:
            file.write(f"{row[0]};{row[1]}\n")

def write_index(data):
    with open("poi_index.csv", "w") as file:
        file.write("ID;Lat;Lon\n")
        for row in data:
            file.write(f"{row[0]};{row[1]};{row[2]}\n")

if __name__ == "__main__":
    DB = "./niedersachsen.sqlite"
    
    print("start reading poi_index...")
    poi_index = read(DB, "poi_index")
    print("    finished")
    print("start reading poi_category_map...")
    poi_category_map = read(DB, "poi_category_map")
    print("    finished")

    print("joining poi...")
    poi = join_category_points(poi_index, poi_category_map)
    print("    finished")

    print("extracting locations...")
    filt = read_filter_polygon("./niedersachsen_buffer.json")
    locs = extract_locations(poi, filt)
    print("    finished")

    print("start writing facilities...")
    write_facilities(locs)
    print("    finished")
    print("start writing physicans...")
    write_physicians(locs)
    print("    finished")
