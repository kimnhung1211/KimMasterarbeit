import datetime
from utils import helper
import pandas as pd
import config


class Stop(object):
    stop_id = str
    stop_lat = float
    stop_lon = float
    stop_name = str
    operator = str

    def __repr__(self):
        return "Stop ID " + str(self.stop_id)

    def __init__(self, stop_id, stop_lat, stop_lon, stop_name, operator):
        self.stop_id = stop_id
        self.stop_lat = float(stop_lat)
        self.stop_lon = float(stop_lon)
        self.stop_name = stop_name
        self.operator = operator


class Trip(object):
    trip_id = str
    route_id = str
    stops_list = list
    stop_times_list = list
    route_type = str

    def __repr__(self):
        return "Trip ID " + str(self.trip_id)

    def __init__(self, trip_id, route_id, stops_list, stop_times_list, route_type):
        self.trip_id = trip_id
        self.route_id = route_id
        self.stops_list = stops_list
        self.stop_times_list = stop_times_list
        self.route_type = route_type
        self.convert_stop_times_to_datetime()

    def convert_stop_times_to_datetime(self):
        converted_stop_times_list = []
        for time_info in self.stop_times_list:
            if int(time_info[0].split(':')[0]) >= 24:
                current_date = '2018-01-02 '
                arr_time_str = str(int(time_info[0].split(
                    ':')[0]) % 24) + ':' + time_info[0].split(':')[1] + ':' + \
                    time_info[0].split(':')[2]
            else:
                current_date = '2018-01-01 '
                arr_time_str = time_info[0]

            date_time_str_arr = current_date + arr_time_str
            date_time_obj_arr = datetime.datetime.strptime(
                date_time_str_arr, '%Y-%m-%d %H:%M:%S')

            if int(time_info[1].split(':')[0]) >= 24:
                current_date = '2018-01-02 '
                dep_time_str = str(int(time_info[1].split(
                    ':')[0]) % 24) + ':' + time_info[1].split(':')[1] + ':' + \
                    time_info[1].split(':')[2]
            else:
                current_date = '2018-01-01 '
                dep_time_str = time_info[1]

            date_time_str_dep = current_date + dep_time_str
            date_time_obj_dep = datetime.datetime.strptime(
                date_time_str_dep, '%Y-%m-%d %H:%M:%S')
            converted_stop_times_list.append(
                [date_time_obj_arr, date_time_obj_dep])
        self.stop_times_list = converted_stop_times_list


class Search_Request(object):
    earliest_departure = datetime.datetime
    departure_lat = float
    departure_lon = float
    arrival_lat = float
    arrival_lon = float

    def __repr__(self):
        return str(self.earliest_departure) + " - " + str(self.departure_lat) \
            + " - " + str(self.departure_lon)

    def __init__(self, earliest_departure, departure_lat, departure_lon,
                 arrival_lat, arrival_lon, city, sampling_method,
                 number_of_sampling_intervals):
        self.earliest_departure = earliest_departure
        self.departure_lat = departure_lat
        self.departure_lon = departure_lon
        self.arrival_lat = arrival_lat
        self.arrival_lon = arrival_lon
        self.city = city
        self.sampling_method = sampling_method
        self.number_of_sampling_intervals = number_of_sampling_intervals
        assert self.validate(), "Wrong Data Type!"

    def validate(self):
        if isinstance(self.earliest_departure, datetime.datetime) and \
                isinstance(self.departure_lat, float) and \
            isinstance(self.departure_lon, float) and \
                isinstance(self.arrival_lat, float) and \
                isinstance(self.arrival_lon, float):
            return True
        else:
            return False


class Itinerary(object):
    itinerary_id = str
    price = float
    travel_time = float
    number_of_transfer = int
    schedule_df = None

    def __repr__(self):
        return self.itinerary_id + " - " + str(round(self.price, 1)) + " Euros " \
            + " - " + str(round(self.travel_time/3600, 1)) + " Hours " \
            + " - " + str(self.number_of_transfer) + " Transfer " \


    def __init__(self, G, path, itinerary_id):
        self.itinerary_id = itinerary_id
        self.price = helper.path_length(G, path, 'price')
        self.travel_time = helper.path_length(G, path, 'travel_time')
        self.number_of_transfer = helper.path_length(G, path, 'transfer')
        self.schedule_df = self.create_itinerary_segments(G, path)

    def create_itinerary_segments(self, G, path):
        number_of_node = len(path)
        actions = []
        durations = []
        from_stops = []
        to_stops = []
        vehicles = []
        for index, node in enumerate(path):
            if index == number_of_node - 1:
                continue

            if index == 0:
                action = "Walk"
                duration = G[path[index]][path[index+1]]['travel_time']
                from_stop = 'Start Location'
                to_stop = G.nodes[path[index+1]]['stop_name']
                vehicle = "FOOT"

            elif index == number_of_node - 2:
                action = "Walk"
                duration = G[path[index]][path[index+1]]['travel_time']
                from_stop = G.nodes[path[index]]['stop_name']
                to_stop = 'End Location'
                vehicle = "FOOT"

            elif G.nodes[path[index]]['trip_id'] \
                    == G.nodes[path[index+1]]['trip_id']:
                if G.nodes[path[index]]['stop_name'] \
                        != G.nodes[path[index+1]]['stop_name']:
                    action = "Ride"
                else:
                    action = "Stay On Vehicle"
                duration = G[path[index]][path[index+1]]['travel_time']
                from_stop = G.nodes[path[index]]['stop_name']
                to_stop = G.nodes[path[index+1]]['stop_name']
                vehicle = G.nodes[path[index+1]]['vehicle_type'] \
                    + G.nodes[path[index+1]]['trip_id']

            elif G.nodes[path[index]]['trip_id'] \
                    != G.nodes[path[index+1]]['trip_id']:
                action = "Transfer"
                duration = G[path[index]][path[index+1]]['travel_time']
                from_stop = G.nodes[path[index]]['stop_name']
                to_stop = G.nodes[path[index+1]]['stop_name']
                vehicle = "FOOT"

            actions.append(action)
            durations.append(round(duration/60, 1))
            from_stops.append(from_stop)
            to_stops.append(to_stop)
            vehicles.append(vehicle)

            itinerary_df = pd.DataFrame(
                {'Action': actions,
                 'Duration': durations,
                 'From': from_stops,
                 'To': to_stops,
                 'Vehicle': vehicles,
                 })
        return itinerary_df


class SamplingInterval(object):
    lower_limit = float
    upper_limit = float
    current_solutions = list
    hv_contributed_time = int
    blacklisted = bool
    original_upper_limit = float
    original_lower_limit = float
    score = 0

    def __init__(self, lower_limit, upper_limit,
                 current_solutions, hv_contributed_time):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.current_solutions = current_solutions
        self.hv_contributed_time = hv_contributed_time
        self.blacklisted = False
        self.original_lower_limit = lower_limit
        self.original_upper_limit = upper_limit
        self.score = 0

    def __repr__(self):
        return "Interval Range: " + \
            str(self.lower_limit) + "|" + str(self.upper_limit)

    def update_interval(self, solution, current_interval):
        wrong_interval = False
        if solution.travel_time < self.lower_limit or \
                solution.travel_time > self.upper_limit:
            wrong_interval = True

        if (solution.travel_time < self.lower_limit or
                solution.travel_time > self.upper_limit or
                solution.nodes_list in
            [s.nodes_list for s in self.current_solutions]) \
                and current_interval == True:
            self.blacklisted = True
            print("Interval is blacklisted!")
        else:
            if solution.nodes_list not in \
                    [s.nodes_list for s in self.current_solutions]:
                self.current_solutions.append(solution)
                self.upper_limit = max(self.lower_limit, min(
                    [s.travel_time-1 for s in self.current_solutions]))
            if self.upper_limit == self.lower_limit \
                    and current_interval == True:
                self.blacklisted = True
                print("Interval is blacklisted!")
        self.current_solutions.sort(key=lambda x: x.travel_time, reverse=False)
        return wrong_interval


class Solution(object):
    travel_time = float
    price = float
    nodes_list = list

    def __init__(self, travel_time, price, nodes_list):
        self.travel_time = travel_time
        self.price = price
        self.nodes_list = nodes_list
