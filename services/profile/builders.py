# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

import numpy as np
import pyaccess

def build_driving_car(osm_file: str, store: bool = False, store_dir: str = "") -> pyaccess.Graph:
    nodes, edges = pyaccess.parse_osm(osm_file, "driving")
    graph = pyaccess.new_graph(nodes, edges)
    # optimize graph
    unconnected = pyaccess.calc_unconnected_nodes(graph)
    graph.remove_nodes(unconnected)
    pyaccess.util.remove_graph_nodes(nodes, edges, unconnected)
    ordering = pyaccess.calc_dfs_ordering(graph)
    graph.reorder_nodes(ordering)
    pyaccess.util.reorder_graph_data(nodes, edges, ordering)
    # build weighting
    weight = pyaccess.build_fastest_weighting(graph, edges)
    graph.add_weighting("time", weight)
    # store graph
    if store:
        graph.store("driving-car", store_dir)
        nodes.to_feather(f"{store_dir}/driving-car-nodes")
        edges.to_feather(f"{store_dir}/driving-car-edges")
    return graph

def build_walking_foot(osm_file: str, store: bool = False, store_dir: str = "") -> pyaccess.Graph:
    nodes, edges = pyaccess.parse_osm(osm_file, "walking")
    graph = pyaccess.new_graph(nodes, edges)
    # optimize graph
    unconnected = pyaccess.calc_unconnected_nodes(graph)
    graph.remove_nodes(unconnected)
    pyaccess.util.remove_graph_nodes(nodes, edges, unconnected)
    ordering = pyaccess.calc_dfs_ordering(graph)
    graph.reorder_nodes(ordering)
    pyaccess.util.reorder_graph_data(nodes, edges, ordering)
    # build weighting
    weight = pyaccess.build_fastest_weighting(graph, edges)
    graph.add_weighting("time", weight)
    # store graph
    if store:
        graph.store("walking-foot", store_dir)
        nodes.to_feather(f"{store_dir}/walking-foot-nodes")
        edges.to_feather(f"{store_dir}/walking-foot-edges")
    return graph

def build_public_transit(graph: pyaccess.Graph, gtfs_dir: str, gtfs_filter_polygon, store: bool = False, store_dir: str = "") -> pyaccess.Graph:
    stops, conns, schedules = pyaccess.parse_gtfs(gtfs_dir, gtfs_filter_polygon)
    graph.add_public_transit("transit", stops, conns, weight="time")
    for day, schedule in schedules.items():
        weight = pyaccess.new_transit_weighting(graph, "transit")
        for i, conn in enumerate(schedule):
            weight.set_connection_schedule(i, conn)
        graph.add_transit_weighting(day, weight, "transit")
    if store:
        graph.store()
    return graph
