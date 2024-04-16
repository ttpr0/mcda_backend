# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from typing import Any

from shapely import from_wkb, Point

def read_population(filename: str) -> list[dict[str, Any]]:
    print("reading population data")
    population_data = []
    with open(filename, 'r') as file:
        delimiter = ';'
        line = file.readline()
        tokens = line.split(delimiter)
        # population indices
        index_ew_gesamt = -1
        index_stnd00_09 = -1
        index_stnd10_19 = -1
        index_stnd20_39 = -1
        index_stnd40_59 = -1
        index_stnd60_79 = -1
        index_stnd80x = -1
        index_kisc00_02 = -1
        index_kisc03_05 = -1
        index_kisc06_09 = -1
        index_kisc10_14 = -1
        index_kisc15_17 = -1
        index_kisc18_19 = -1
        index_kisc20x = -1
        # geom indices
        index_geom = -1
        index_geom_utm = -1
        for i, token in enumerate(tokens):
            if token == "EW_GESAMT":
                index_ew_gesamt = i
            if token == "GEOM":
                index_geom = i
            if token == "GEOM_UTM":
                index_geom_utm = i
            if token == "STND00_09":
                index_stnd00_09 = i
            if token == "STND10_19":
                index_stnd10_19 = i
            if token == "STND20_39":
                index_stnd20_39 = i
            if token == "STND40_59":
                index_stnd40_59 = i
            if token == "STND60_79":
                index_stnd60_79 = i
            if token == "STND80X":
                index_stnd80x = i
            if token == "KITA_SCHUL":
                index_kisc00_02 = i
            if token == "KITA_SC_01":
                index_kisc03_05 = i
            if token == "KITA_SC_02":
                index_kisc06_09 = i
            if token == "KITA_SC_03":
                index_kisc10_14 = i
            if token == "KITA_SC_04":
                index_kisc15_17 = i
            if token == "KITA_SC_05":
                index_kisc18_19 = i
            if token == "KITA_SC_06":
                index_kisc20x = i
        while True:
            line = file.readline()
            if not line:
                break
            tokens = line.split(delimiter)
            point: Point = from_wkb(bytes.fromhex(tokens[index_geom]))
            utm_point: Point = from_wkb(bytes.fromhex(tokens[index_geom_utm]))
            attr = {
                "wgs_x": point.x,
                "wgs_y": point.y,
                "utm_x": utm_point.x,
                "utm_y": utm_point.y,
            }
            attr["ew_gesamt"] = int(float(tokens[index_ew_gesamt].replace(",", ".")))
            attr["std_00_09"] = int(float(tokens[index_stnd00_09].replace(",", ".")))
            attr["std_10_19"] = int(float(tokens[index_stnd10_19].replace(",", ".")))
            attr["std_20_39"] = int(float(tokens[index_stnd20_39].replace(",", ".")))
            attr["std_40_59"] = int(float(tokens[index_stnd40_59].replace(",", ".")))
            attr["std_60_79"] = int(float(tokens[index_stnd60_79].replace(",", ".")))
            attr["std_80x"] = int(float(tokens[index_stnd80x].replace(",", ".")))
            attr["ksc_00_02"] = int(float(tokens[index_kisc00_02].replace(",", ".")))
            attr["ksc_03_05"] = int(float(tokens[index_kisc03_05].replace(",", ".")))
            attr["ksc_06_09"] = int(float(tokens[index_kisc06_09].replace(",", ".")))
            attr["ksc_10_14"] = int(float(tokens[index_kisc10_14].replace(",", ".")))
            attr["ksc_15_17"] = int(float(tokens[index_kisc15_17].replace(",", ".")))
            attr["ksc_18_19"] = int(float(tokens[index_kisc18_19].replace(",", ".")))
            attr["ksc_20x"] = int(float(tokens[index_kisc20x].replace(",", ".")))
            population_data.append(attr)
    return population_data

def write_to_csv(filename: str, data: list[dict[str, Any]]):
    with open(filename, "w") as file:
        headers = [key for key in data[0].keys()]
        file.write(';'.join(headers) + "\n")
        for item in data:
            line = [str(item[x]) for x in headers]
            file.write(';'.join(line) + "\n")

if __name__ == "__main__":
    data = read_population("./files/population.csv")
    write_to_csv("./files/population_niedersachsen.csv", data)
