import config
import entites
import re
import csv


def import_stops(operator_name):
    if operator_name == 'FLIX':
        path = config.fb_gtfs_path
    elif operator_name == 'DB':
        path = config.db_gtfs_path

    stops_list = []
    with open(path + '\\stops.txt', encoding="utf8") as stops_file:
        lines = [line.rstrip() for line in stops_file]
        for index, line in enumerate(csv.reader(lines, quotechar='"',
                                                delimiter=',',
                                                quoting=csv.QUOTE_ALL,
                                                skipinitialspace=True)):
            if index == 0:
                continue
            else:
                if operator_name == 'FLIX':
                    stop = entites.Stop(
                        line[0], line[4], line[5], line[2], operator_name)
                    stops_list.append(stop)
                elif operator_name == 'DB':
                    stop = entites.Stop(
                        line[0], line[2], line[3], line[1], operator_name)
                    stops_list.append(stop)
    return stops_list


def import_stop_times(operator_name):
    if operator_name == 'FLIX':
        path = config.fb_gtfs_path
    elif operator_name == 'DB':
        path = config.db_gtfs_path

    with open(path + '\\stop_times.txt', encoding="utf8") as stop_times_file:
        lines = [line.rstrip() for line in stop_times_file]
        stop_times_dict = {}
        for index, line in enumerate(csv.reader(lines, quotechar='"',
                                                delimiter=',',
                                                quoting=csv.QUOTE_ALL,
                                                skipinitialspace=True)):
            if index == 0:
                continue
            else:
                if line[0] not in stop_times_dict:
                    stop_times_dict[line[0]] = [
                        [line[1], line[2], line[3], line[4]]]
                else:
                    stop_times_dict[line[0]].append(
                        [line[1], line[2], line[3], line[4]])
    return stop_times_dict


def import_trips(operator_name, stop_times_dict, stops_list, route_type_dict):
    if operator_name == 'FLIX':
        path = config.fb_gtfs_path
    elif operator_name == 'DB':
        path = config.db_gtfs_path

    trips_list = []
    with open(path + '\\trips.txt', encoding="utf8") as trips_file:
        lines = [line.rstrip() for line in trips_file]
        for index, line in enumerate(csv.reader(lines, quotechar='"',
                                                delimiter=',',
                                                quoting=csv.QUOTE_ALL,
                                                skipinitialspace=True)):
            if line[2].find("Z-") != -1:
                continue
            
            if index == 0:
                continue
            else:
                relevant_stop_ids = [item[2]
                                     for item in stop_times_dict[line[2]]]
                relevant_stop_times = [[item[0], item[1]]
                                       for item in stop_times_dict[line[2]]]
                relevant_stops = []
                for st_id in relevant_stop_ids:
                    relevant_stops.append(
                        [stop for stop in stops_list if stop.stop_id == st_id][0])
                trip = entites.Trip(
                    line[2], line[0], relevant_stops, relevant_stop_times, route_type_dict[line[0]])
                trips_list.append(trip)
    return trips_list


def import_routes(operator_name):
    if operator_name == 'FLIX':
        path = config.fb_gtfs_path
    elif operator_name == 'DB':
        path = config.db_gtfs_path

    with open(path + '\\routes.txt', encoding="utf8") as stop_times_file:
        lines = [line.rstrip() for line in stop_times_file]
        route_type_dict = {}
        for index, line in enumerate(csv.reader(lines, quotechar='"',
                                                delimiter=',',
                                                quoting=csv.QUOTE_ALL,
                                                skipinitialspace=True)):
            if index == 0:
                continue
            else:
                if operator_name == 'FLIX':
                    route_type_dict[line[0]] = 'FLIXBUS'
                elif operator_name == 'DB':
                    route_type_dict[line[0]] = define_route_type(line[2])
    return route_type_dict


def import_total(operator_name):
    stops_list = import_stops(operator_name)
    stop_times_dict = import_stop_times(operator_name)
    route_type_dict = import_routes(operator_name)
    trips_list = import_trips(
        operator_name, stop_times_dict, stops_list, route_type_dict)
    print('Done importing for service provider: ', operator_name)
    return trips_list


def define_route_type(long_route_name):
    if (long_route_name.lower().find("ice") == 0) or \
        (long_route_name.lower().find("d") == 0):
        route_type = "DBICE"

    elif (long_route_name.lower().find("ic") == 0) or \
        (long_route_name.lower().find("nj") == 0) or \
            (long_route_name.lower().find("ec") == 0) or \
                (long_route_name.lower().find("tgv") == 0) or \
                    (long_route_name.lower().find("rj") == 0) or \
                        (long_route_name.lower().find("en") == 0):
        route_type = "DBIC"
    
    else: route_type = "DBRegio"
    
    return route_type