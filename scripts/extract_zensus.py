# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import re
from pyproj import Transformer

def read_zenus(filename: str) -> dict:
    # maps cell-codes to population-data
    data = {}
    with open(filename, "r") as file:
        header = file.readline()
        tokens = header.split(";")
        key_index, feature_index, code_index, count_index = None, None, None, None
        for i, token in enumerate(tokens):
            if token == "Gitter_ID_100m_neu":
                key_index = i
            if token == "Merkmal":
                feature_index = i
            if token == "Auspraegung_Code":
                code_index = i
            if token == "Anzahl":
                count_index = i
        if key_index is None or feature_index is None or code_index is None or count_index is None:
            raise ValueError("invalid Zensus file!")
        for line in file.readlines():
            tokens = line.split(";")
            grid_key = tokens[key_index]
            feature = tokens[feature_index]
            if feature != "ALTER_10JG" and feature != "ALTER_KURZ":
                    continue
            code = int(tokens[code_index])
            count = int(tokens[count_index])
            if grid_key not in data:
                item = {}
            else:
                item = data[grid_key]
            if feature not in item:
                if feature == "ALTER_10JG":
                    content = [0] * 9
                else:
                    content = [0] * 5
            else:
                content = item[feature]
            content[code-1] = count
            item[feature] = content
            data[grid_key] = item
    return data

wgs_transformer = Transformer.from_crs(3035, 4326, always_xy=True)
utm_transformer = Transformer.from_crs(3035, 25832, always_xy=True)

def get_locations(key: str) -> tuple[float, float, float, float]:
    tokens = re.split("CRS|RES|N|E", key)
    crs = int(tokens[1])
    if crs != 3035:
        raise ValueError("invalid CRS!")
    north = int(tokens[3])
    east = int(tokens[4])
    wgs_x, wgs_y = wgs_transformer.transform(east, north)
    utm_x, utm_y = utm_transformer.transform(east, north)
    return wgs_x, wgs_y, utm_x, utm_y

def write_to_csv(filename: str, data: dict):
    groups = {
        "ALTER_10JG": ["std_00_09", "std_10_19", "std_20_29", "std_30_39", "std_40_49", "std_50_59", "std_60_69", "std_70_79", "std_80x"],
        "ALTER_KURZ": ["short_00_17", "short_18_29", "short_30_49", "short_50_64", "short_65x"],
    }
    with open(filename, "w") as file:
        headers = ["wgs_x", "wgs_y", "utm_x", "utm_y"]
        for group in groups:
            for key in groups[group]:
                headers.append(key)
        file.write(';'.join(headers) + "\n")
        for key, item in data.items():
            line = [str(x) for x in get_locations(key)]
            for group in groups:
                if group not in item:
                    if group == "ALTER_10JG":
                        c = 9
                    else:
                        c = 5
                    for i in range(c):
                        line.append("0")
                    continue
                for val in item[group]:
                    line.append(str(val))
            file.write(';'.join(line) + "\n")


if __name__ == "__main__":
    data = read_zenus("D:/Daten/csv_Demographie_100_Meter-Gitter/Bevoelkerung100M.csv")
    write_to_csv("./files/population_germany.csv", data)
