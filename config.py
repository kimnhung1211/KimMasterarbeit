import datetime

db_gtfs_path = 'gtfsdata\\db_gtfs'
fb_gtfs_path = 'gtfsdata\\flixbus_gtfs'

large_constant = 10000000
walking_speed = 5  # (km/hour)
max_possible_speed = 300  # (km/hour)

# Price config
price_per_km_DBRegio = 0.17
price_per_km_DBIC = 0.17 * 1.5
price_per_km_DBICE = 0.17 * 2
price_per_km_FLIXBUS = 0.10


# Search request config
max_time_from_earliest_departure = 10*60*60  # (seconds)
max_arrival_time_from_earliest_departure = 10*60*60  # (seconds)
max_walking_distance = 0.5  # (kilometer)


# Objective config
primary_objective_name = 'weight'
secondary_objective_name = 'res_cost'

# Normalization factor to calculate hypervolume
# 360 seconds worth 1 Euros in hypervolume contribution
hv_normalization_factor = 360

# Multi-armed bandit configuration
epsilon = 0.2

start_node_name = 'Source'
end_node_name = 'Sink'


search_request_list =\
    [[datetime.datetime(2018, 1, 1, 5, 0), 48.784081, 9.181636,
      51.517899, 7.459294, 'STUT_DORT', 'mab', 5],
     [datetime.datetime(2018, 1, 1, 5, 0), 48.784081, 9.181636,
      51.517899, 7.459294, 'STUT_DORT', 'mab', 10],
     [datetime.datetime(2018, 1, 1, 5, 0), 48.784081, 9.181636,
      51.517899, 7.459294, 'STUT_DORT', 'systemic', 5],
     [datetime.datetime(2018, 1, 1, 5, 0), 48.784081, 9.181636,
      51.517899, 7.459294, 'STUT_DORT', 'systemic', 10],
     [datetime.datetime(2018, 1, 1, 5, 0), 50.943029, 6.95873,
      52.525589, 13.369549, 'COL_BER', 'mab', 5],
     [datetime.datetime(2018, 1, 1, 5, 0), 50.943029, 6.95873,
      52.525589, 13.369549, 'COL_BER', 'mab', 10],
     [datetime.datetime(2018, 1, 1, 5, 0), 50.943029, 6.95873,
      52.525589, 13.369549, 'COL_BER', 'systemic', 5],
     [datetime.datetime(2018, 1, 1, 5, 0), 50.943029, 6.95873,
      52.525589, 13.369549, 'COL_BER', 'systemic', 10]]
