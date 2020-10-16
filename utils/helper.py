import networkx as nx
from itertools import islice
from haversine import haversine, haversine_vector
import config
from datetime import timedelta
import numpy as np
import path_finder
import entites
from hv import HyperVolume


def path_length(G, nodes, weight):
    w = 0
    for ind, nd in enumerate(nodes[1:]):
        prev = nodes[ind]
        w += G[prev][nd][weight]
    return w


def k_shortest_paths(G, source, target, k, weight=None):
    return list(islice(nx.shortest_simple_paths(G, source, target,
                                                weight=weight), k))


def add_search_request_to_graph(G, search_request):
    departure_nodes = relevant_departure_node_id(G, search_request)
    arrival_nodes = None
    if departure_nodes:
        arrival_nodes = relevant_arrival_node_id(
            G, search_request, departure_nodes)
    if arrival_nodes:
        G = add_dummy_start_node(
            G, departure_nodes, search_request)
        G = add_dummy_end_node(
            G, arrival_nodes, search_request)
    return departure_nodes, arrival_nodes, G


def add_dummy_end_node(G, arrival_nodes, search_request):
    G.add_node(config.end_node_name,
               trip_id="dummy",
               stop_name="dummy",
               node_type="dummy",
               vehicle_type="dummy",
               stop_lat="dummy",
               stop_lon="dummy",
               time="dummy")
    for arr_node in arrival_nodes:
        arr_node_lat = [node for node in G.nodes(
            data=True) if node[0] == arr_node][0][1]['stop_lat']
        arr_node_lon = [node for node in G.nodes(
            data=True) if node[0] == arr_node][0][1]['stop_lon']
        walking_distance = haversine(
            (search_request.arrival_lat, search_request.arrival_lon),
            (arr_node_lat, arr_node_lon))
        walking_time_in_seconds = (
            walking_distance/config.walking_speed)*3600
        G.add_edge(arr_node,
                   config.end_node_name,
                   res_cost=np.array([walking_time_in_seconds]),
                   weight=0,
                   transfer=0)
    return G


def add_dummy_start_node(G, departure_nodes, search_request):
    G.add_node(config.start_node_name,
               trip_id="dummy",
               stop_name="dummy",
               node_type="dummy",
               vehicle_type="dummy",
               stop_lat="dummy",
               stop_lon="dummy",
               time="dummy")
    for dep_node in departure_nodes:
        dep_node_lat = [node for node in G.nodes(
            data=True) if node[0] == dep_node][0][1]['stop_lat']
        dep_node_lon = [node for node in G.nodes(
            data=True) if node[0] == dep_node][0][1]['stop_lon']
        walking_distance = haversine(
            (search_request.departure_lat, search_request.departure_lon),
            (dep_node_lat, dep_node_lon))
        walking_time_in_seconds = (
            walking_distance/config.walking_speed)*3600
        G.add_edge(config.start_node_name,
                   dep_node,
                   res_cost=np.array([walking_time_in_seconds]),
                   weight=0,
                   transfer=0)
    return G


def relevant_departure_node_id(G, search_request):

    relevant_nodes_id = []

    source_coor = [search_request.departure_lat,
                   search_request.departure_lon]

    earliest_departure = search_request.earliest_departure

    node_label_list = [u[0] for u in G.nodes(data=True)]

    node_type_list = [u[1]['node_type']
                      for u in G.nodes(data=True)]

    depature_time_list = [u[1]['time']
                          for u in G.nodes(data=True)]

    sink_array = np.array([[v[1]['stop_lat'], v[1]['stop_lon']]
                           for v in G.nodes(data=True)])

    distance_array = haversine_vector(source_coor, sink_array)
    valid_indexes = np.where(distance_array <=
                             config.max_walking_distance)[0].tolist()

    for t in valid_indexes:
        if node_type_list[t] == "departure":
            walking_time_in_seconds = (
                distance_array[t]/config.walking_speed)*3600
            if earliest_departure + timedelta(seconds=walking_time_in_seconds) \
                <= depature_time_list[t] and \
                    (depature_time_list[t]-earliest_departure).seconds <= \
                config.max_time_from_earliest_departure:
                relevant_nodes_id.append(node_label_list[t])

    return relevant_nodes_id


def relevant_arrival_node_id(G, search_request, departure_nodes):

    relevant_nodes_id = []

    request_flying_distance = haversine((search_request.departure_lat,
                                         search_request.departure_lon),
                                        (search_request.arrival_lat,
                                         search_request.arrival_lon))

    request_flying_time = (request_flying_distance /
                           config.max_possible_speed)*3600

    source_coor = [search_request.arrival_lat,
                   search_request.arrival_lon]

    earliest_departure = search_request.earliest_departure

    node_label_list = [u[0] for u in G.nodes(data=True)]

    node_type_list = [u[1]['node_type']
                      for u in G.nodes(data=True)]

    arrival_time_list = [u[1]['time']
                         for u in G.nodes(data=True)]

    sink_array = np.array([[v[1]['stop_lat'], v[1]['stop_lon']]
                           for v in G.nodes(data=True)])

    distance_array = haversine_vector(source_coor, sink_array)
    valid_indexes = np.where(distance_array <=
                             config.max_walking_distance)[0].tolist()

    for t in valid_indexes:
        if node_type_list[t] == "arrival" and \
            (arrival_time_list[t] >= earliest_departure +
                timedelta(seconds=request_flying_time)) \
            and (arrival_time_list[t] <= earliest_departure +
                 timedelta(
                seconds=config.max_arrival_time_from_earliest_departure)):
            relevant_nodes_id.append(node_label_list[t])

    return relevant_nodes_id


def create_intervals_list(G, number_of_intervals):
    intervals_list = []

    top_left_solution, bottom_right_solution = find_extreme_solutions(G)

    max_travel_time = bottom_right_solution.travel_time
    min_travel_time = top_left_solution.travel_time

    interval_length = (max_travel_time - min_travel_time) / number_of_intervals

    current_range_low = min_travel_time

    for i in range(number_of_intervals):
        current_interval = entites.SamplingInterval(
            current_range_low, current_range_low+interval_length, [], 0)
        intervals_list.append(current_interval)
        current_range_low += interval_length
    return intervals_list, top_left_solution, bottom_right_solution


def find_extreme_solutions(G):
    top_left_path = path_finder.find_shortest_path(G, config.start_node_name,
                                                   config.end_node_name,
                                                   config.secondary_objective_name)
    top_left_travel_time = path_length(
        G, top_left_path, config.secondary_objective_name)[0]
    top_left_price = path_length(
        G, top_left_path, config.primary_objective_name)
    top_left_solution = entites.Solution(
        top_left_travel_time, top_left_price, top_left_path)

    bottom_right_path = path_finder.find_shortest_path(G, config.start_node_name,
                                                       config.end_node_name,
                                                       config.primary_objective_name)
    bottom_right_travel_time = path_length(
        G, bottom_right_path, config.secondary_objective_name)[0]
    bottom_right_price = path_length(
        G, bottom_right_path, config.primary_objective_name)
    bottom_right_solution = entites.Solution(
        bottom_right_travel_time, bottom_right_price, bottom_right_path)

    return top_left_solution, bottom_right_solution


def calculate_hypervolume_nomalization_factor(G):
    max_travel_time = path_length(
        G, path_finder.find_shortest_path(G, config.start_node_name,
                                          config.end_node_name,
                                          config.primary_objective_name),
        config.secondary_objective_name)[0]

    max_price = path_length(
        G, path_finder.find_shortest_path(G, config.start_node_name,
                                          config.end_node_name,
                                          config.secondary_objective_name),
        config.primary_objective_name)

    hv_reference_point = [max_travel_time*1.1 /
                          config.hv_normalization_factor, max_price*1.1]

    return hv_reference_point
