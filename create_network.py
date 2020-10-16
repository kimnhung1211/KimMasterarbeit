import networkx as nx
from haversine import haversine, haversine_vector
import config
from datetime import timedelta
from itertools import permutations
import numpy as np
import sys
import random


def create_time_expanded_network(trips_list):
    G = nx.DiGraph(n_res=1)
    for trip in trips_list:
        for index, current_stop in enumerate(trip.stops_list):
            current_node_id = trip.route_type + '-' + \
                trip.trip_id + '-' + current_stop.stop_id
            current_lat = current_stop.stop_lat
            current_lon = current_stop.stop_lon

            G.add_node("arrival_" + current_node_id,
                       trip_id=trip.trip_id,
                       stop_name=current_stop.stop_name,
                       node_type="arrival",
                       vehicle_type=trip.route_type,
                       stop_lat=current_stop.stop_lat,
                       stop_lon=current_stop.stop_lon,
                       time=trip.stop_times_list[index][0])

            G.add_node("departure_" + current_node_id,
                       trip_id=trip.trip_id,
                       stop_name=current_stop.stop_name,
                       node_type="departure",
                       vehicle_type=trip.route_type,
                       stop_lat=current_stop.stop_lat,
                       stop_lon=current_stop.stop_lon,
                       time=trip.stop_times_list[index][1])

            G.add_edge("arrival_" + current_node_id,
                       "departure_" + current_node_id,
                       res_cost=np.array([(trip.stop_times_list[index][1] -
                                           trip.stop_times_list[index][0]).seconds]),
                       weight=0,
                       transfer=0)

            if index == 0:
                previous_dep_time = trip.stop_times_list[index][1]
                preivous_node_id = current_node_id
                previous_lat = current_lat
                previous_lon = current_lon
            else:
                travel_time_in_seconds = (trip.stop_times_list[index][0] -
                                          previous_dep_time).seconds
                air_distance_in_kms = haversine((current_lat, current_lon),
                                                (previous_lat, previous_lon))
                price = determine_price(air_distance_in_kms,
                                        trip.route_type)

                G.add_edge("departure_" + preivous_node_id,
                           "arrival_" + current_node_id,
                           res_cost=np.array([travel_time_in_seconds]),
                           weight=price,
                           transfer=0)
                previous_dep_time = trip.stop_times_list[index][1]
                preivous_node_id = current_node_id
                previous_lat = current_lat
                previous_lon = current_lon
    G = create_transfer_edges(G)
    return G


def create_transfer_edges(G):
    source_coordinates = [[u[1]['stop_lat'], u[1]['stop_lon']]
                          for u in G.nodes(data=True)]
    sink_coordinates = [[v[1]['stop_lat'], v[1]['stop_lon']]
                        for v in G.nodes(data=True)]
    node_label_list = [u[0] for u in G.nodes(data=True)]
    node_type_list = [u[1]['node_type']
                      for u in G.nodes(data=True)]
    node_trip_id_list = [u[1]['trip_id']
                         for u in G.nodes(data=True)]
    arrival_time_list = [u[1]['time']
                         for u in G.nodes(data=True)]
    depature_time_list = [u[1]['time']
                          for u in G.nodes(data=True)]
    source_array = np.array(source_coordinates)
    sink_array = np.array(sink_coordinates)
    for index, source_coor in enumerate(source_array):
        distance_array = haversine_vector(source_coor, sink_array)
        valid_indexes = np.where(distance_array <=
                                 config.max_walking_distance)[0].tolist()
        for t in valid_indexes:
            if node_type_list[index] == "arrival" \
                and node_type_list[t] == "departure" \
                    and node_trip_id_list[index] != node_trip_id_list[t]:
                travel_time_in_seconds = (
                    distance_array[t]/config.walking_speed)*3600
                total_transfer_time_in_second = (
                    depature_time_list[t] - arrival_time_list[index]).seconds
                if arrival_time_list[index] + \
                        timedelta(seconds=travel_time_in_seconds) \
                    <= depature_time_list[t] and \
                        node_label_list[index] != node_label_list[t]:
                    G.add_edge(node_label_list[index], node_label_list[t],
                               res_cost=np.array(
                                   [total_transfer_time_in_second]),
                               weight=0,
                               transfer=1)
    return G


def determine_price(distance, route_type):
    assert route_type in \
        ["DBRegio", "DBICE", "DBIC", "FLIXBUS"], "No route type found!"

    if route_type == "DBRegio":
        return distance*config.price_per_km_DBRegio*random.uniform(1.1, 1.3)
    elif route_type == "DBIC":
        return distance*config.price_per_km_DBIC*random.uniform(1.1, 1.3)
    elif route_type == "DBICE":
        return distance*config.price_per_km_DBICE*random.uniform(1.1, 1.3)
    else:
        return distance*config.price_per_km_FLIXBUS*random.uniform(1.1, 1.3)
