from folium.features import DivIcon
from collections import namedtuple

import folium
import numpy as np
import pandas as pd
from folium.plugins import BeautifyIcon
from folium.plugins import MarkerCluster
from selenium import webdriver
import time
import os
import random
import pathlib


path = os.path.join(str(pathlib.Path(__file__).parent.parent.absolute()),
                    'output')
output_file = 'map_output.html'


def get_arrows(locations, color='#FECBA5', size=6, n_arrows=3):
    """
    Get a list of correctly placed and rotated
    arrows/markers to be plotted

    Parameters
    locations : list of lists of lat lons that represent the
                start and end of the line.
                eg [[41.1132, -96.1993],[41.3810, -95.8021]]
    arrow_color : default is 'blue'
    size : default is 6
    n_arrows : number of arrows to create.  default is 3
    Return
    list of arrows/markers
    """

    Point = namedtuple('Point', field_names=['lat', 'lon'])

    # creating point from our Point named tuple
    p1 = Point(locations[0][0], locations[0][1])
    p2 = Point(locations[1][0], locations[1][1])

    # getting the rotation needed for our marker.
    # Subtracting 90 to account for the marker's orientation
    # of due East(get_bearing returns North)
    rotation = get_bearing(p1, p2) - 90

    # get an evenly space list of lats and lons for our arrows
    # note that I'm discarding the first and last for aesthetics
    # as I'm using markers to denote the start and end
    arrow_lats = np.linspace(p1.lat, p2.lat, n_arrows + 2)[1:n_arrows + 1]
    arrow_lons = np.linspace(p1.lon, p2.lon, n_arrows + 2)[1:n_arrows + 1]

    arrows = []

    # creating each "arrow" and appending them to our arrows list
    for points in zip(arrow_lats, arrow_lons):
        arrows.append(folium.RegularPolygonMarker(location=points,
                                                  fill_color='#18b0b0',
                                                  number_of_sides=3,
                                                  radius=4,
                                                  rotation=rotation,
                                                  fill_opacity=1,
                                                  color='#18b0b0'))
    return arrows


def get_bearing(p1, p2):
    """
    Returns compass bearing from p1 to p2

    Parameters
    p1 : namedtuple with lat lon
    p2 : namedtuple with lat lon

    Return
    compass bearing of type float

    Notes
    Based on https://gist.github.com/jeromer/2005586
    """

    long_diff = np.radians(p2.lon - p1.lon)

    lat1 = np.radians(p1.lat)
    lat2 = np.radians(p2.lat)

    x = np.sin(long_diff) * np.cos(lat2)
    y = (np.cos(lat1) * np.sin(lat2)
         - (np.sin(lat1) * np.cos(lat2)
            * np.cos(long_diff)))
    bearing = np.degrees(np.arctan2(x, y))

    # adjusting for compass bearing
    if bearing < 0:
        return bearing + 360
    return bearing


def visualize_instance(trips_list):
    center_lat = 52.1205333
    center_lon = 11.6276237
    some_map = folium.Map(location=[center_lat, center_lon],
                          tiles='cartodbpositron', control_scale=True, zoom_start=7)

    for trip in trips_list:
        for index, stop in enumerate(trip.stops_list):
            if stop == trip.stops_list[0]:
                next_stop = trip.stops_list[index+1]
                folium.CircleMarker(
                    location=[stop.stop_lat,
                              stop.stop_lon],
                    radius=5,
                    color='green',
                    fill_opacity=0.7,
                    fill_color='green',
                    popup=stop.stop_name + str(trip.stop_times_list[index])
                ).add_to(some_map)
                folium.PolyLine(
                    locations=[[stop.stop_lat, stop.stop_lon],
                               [next_stop.stop_lat, next_stop.stop_lon]],
                    color='grey', popup=trip.trip_id + trip.route_type,
                    weight=1, opacity=0.5).add_to(some_map)

            elif stop == trip.stops_list[-1]:
                folium.CircleMarker(
                    location=[stop.stop_lat,
                              stop.stop_lon],
                    radius=5,
                    color='orange',
                    fill_opacity=0.7,
                    fill_color='orange',
                    popup=stop.stop_name + str(trip.stop_times_list[index])
                ).add_to(some_map)

            else:
                next_stop = trip.stops_list[index+1]
                folium.CircleMarker(
                    location=[stop.stop_lat,
                              stop.stop_lon],
                    radius=2,
                    color='grey',
                    fill_opacity=0.7,
                    fill_color='grey',
                    popup=stop.stop_name + str(trip.stop_times_list[index])
                ).add_to(some_map)
                folium.PolyLine(
                    locations=[[stop.stop_lat, stop.stop_lon],
                               [next_stop.stop_lat, next_stop.stop_lon]],
                    color='grey', popup=trip.trip_id + trip.route_type,
                    weight=1, opacity=0.5).add_to(some_map)

    """ transport_requests_group = folium.Featadd_to(some_map)
    used_buses_list = [bus for bus in buses if bus.schedule]
    for request in transport_requests:
        p1 = [request.start_location.lat,
              request.start_location.lon]
        p2 = [request.end_location.lat,
              request.end_location.lon]

        transport_requests_group.add_child(folium.Marker(
            location=p1,
            icon=BeautifyIcon
            (icon='fa-cloudversify',
             icon_shape='circle',
             number=int(request.passengers),
             spin=True,
             border_width=2,
             border_color='grey',
             text_color='white',
             background_color="#A2C900",
             inner_icon_style="font-size:12px;padding-top:-5px;"
             )))
        transport_requests_group.add_child(folium.PolyLine(
            locations=[p1, p2], color='blue', popup=request.request_id))
        arrows = get_arrows(locations=[p1, p2], n_arrows=1)
        for arrow in arrows:
            transport_requests_group.add_child(arrow)

    marker_cluster = MarkerCluster(
        show=False, name='All Partner Depots').add_to(some_map)

    for depot in depots:
        folium.Marker(
            location=[depot.location.lat, depot.location.lon],
            fill_color='#43d9de',
            radius=5,
            popup=depot.available_buses_dict().values()
        ).add_to(marker_cluster)

    used_buses_group = folium.FeatureGroup(
        name='Used Buses', show=True).add_to(some_map)

    for bus in buses:
        if bus.schedule:
            p1 = [bus.depot.location.lat,
                  bus.depot.location.lon]
            p2 = [bus.schedule[0].start_location.lat,
                  bus.schedule[0].start_location.lon]

            used_buses_group.add_child(folium.PolyLine(
                locations=[p1, p2], color='grey', opacity=0.4,
                popup=("Bus ID: " + str(bus.bus_id) +
                       ": " + str(bus.seats) + " seats")))

            used_buses_group.add_child(folium.CircleMarker(
                location=[bus.depot.location.lat, bus.depot.location.lon],
                radius=8,
                color='orange',
                fill_opacity=0.7,
                fill_color='orange',
                
                popup='Dispatched: ' +
                str([value for value in bus.depot.utilized_buses_dict(
                    used_buses_list).values()])
            ))

            arrows = get_arrows(locations=[p1, p2], n_arrows=1)
            for arrow in arrows:
                used_buses_group.add_child(arrow)

            for index, request in enumerate(bus.schedule):
                if request == bus.schedule[-1]:
                    p1 = [request.start_location.lat,
                          request.start_location.lon]
                    p2 = [request.end_location.lat,
                          request.end_location.lon]
                    used_buses_group.add_child(folium.PolyLine(
                        locations=[p1, p2], color='#71BF44', opacity=0.4,
                        popup=(str(request.request_id) +
                               ": " + str(request.passengers) + " pax")))
                    arrows = get_arrows(locations=[p1, p2], n_arrows=1)
                    for arrow in arrows:
                        used_buses_group.add_child(arrow)
                    used_buses_group.add_child(folium.Marker(
                        location=p1,
                        icon=BeautifyIcon
                        (icon='fa-cloudversify',
                         icon_shape='circle',
                         number=int(request.passengers),
                         spin=True,
                         border_width=2,
                         border_color='grey',
                         text_color='white',
                         background_color="#A2C900",
                         inner_icon_style="font-size:12px;padding-top:-5px;"
                         )))
                    used_buses_group.add_child(folium.CircleMarker(
                        location=p2,
                        radius=4,
                        color='#fd5e53',
                        fill_opacity=0.5,
                        fill_color='#fd5e53'))
                else:
                    p1 = [request.start_location.lat,
                          request.start_location.lon]
                    p2 = [bus.schedule[index + 1].start_location.lat,
                          bus.schedule[index + 1].start_location.lon]
                    used_buses_group.add_child(folium.PolyLine(
                        locations=[p1, p2], color='#71BF44', opacity=0.4,
                        popup=(str(request.request_id) +
                               ": " + str(request.passengers) + " pax")))
                    arrows = get_arrows(locations=[p1, p2], n_arrows=1)
                    for arrow in arrows:
                        used_buses_group.add_child(arrow)
                    used_buses_group.add_child(folium.Marker(
                        location=p1,
                        icon=BeautifyIcon
                        (icon='fa-cloudversify',
                         icon_shape='circle',
                         number=int(request.passengers),
                         spin=True,
                         border_width=1,
                         border_color='grey',
                         text_color='white',
                         background_color="#A2C900",
                         inner_icon_style="font-size:12px;padding-top:-5px;"
                         ))) """
    folium.LayerControl().add_to(some_map)
    some_map.save(output_file)
