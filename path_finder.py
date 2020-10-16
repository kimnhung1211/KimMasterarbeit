import networkx as nx
import config
from utils import helper


def find_shortest_path(G, dummy_start_node,
                       dummy_end_node, criteria):

    try:
        shortest_path = \
            nx.shortest_path(G, source=dummy_start_node,
                                target=dummy_end_node, weight=criteria)
    except:
        return None

    if shortest_path:
        return shortest_path
    else:
        return None
