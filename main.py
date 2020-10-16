import data_import
import create_network
import networkx as nx
import pickle
import argparse
import datetime
import entites
import algorithm
import random
import config

if __name__ == "__main__":

    # Arguments parsing
    parsers = argparse.ArgumentParser()
    parsers.add_argument('--read_from_pickle',
                         dest="read_from_pickle", action='store_true')
    args = parsers.parse_args()
    read_from_pickle = True if args.read_from_pickle else False

    # Create or read NetworkX graph object
    if read_from_pickle:
        with open('./input/mm_graph_data', 'rb') as fp:
            G = pickle.load(fp)
            fp.close()
    else:
        # Reading GTFS data
        db_trip_list = data_import.import_total('DB')
        fb_trip_list = data_import.import_total('FLIX')
        mm_trip_list = db_trip_list + fb_trip_list

        G = create_network.create_time_expanded_network(mm_trip_list)
        with open('./input/mm_graph_data', 'wb') as fp:
            pickle.dump(G, fp)
            fp.close()

    random.seed(123)

    for search_info in config.search_request_list:
        search_request = \
            entites.Search_Request(search_info[0],
                                   search_info[1],
                                   search_info[2],
                                   search_info[3],
                                   search_info[4],
                                   search_info[5],
                                   search_info[6],
                                   search_info[7])
        algorithm.find_the_front(G, search_request)
