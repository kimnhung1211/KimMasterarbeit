from utils import helper
import config
import smart_sampler


def find_the_front(G, search_request):

    # Remove old dummy nodes (if exist) then add the new dummy node to the graph
    # to represent the search request
    source = config.start_node_name
    target = config.end_node_name
    res_name = config.secondary_objective_name
    G.remove_nodes_from([source, target])
    relevant_departure_nodes, relevant_arrival_nodes, G = \
        helper.add_search_request_to_graph(G, search_request)

    if relevant_departure_nodes and relevant_arrival_nodes:
        intervals_list, top_left_solution, \
            bottom_right_solution = helper.create_intervals_list(
                G, search_request.number_of_sampling_intervals)
        hv_reference_point = \
            helper.calculate_hypervolume_nomalization_factor(G)

        Sampler = smart_sampler.SmartSampler(intervals_list, G, res_name,
                                             source, target, hv_reference_point,
                                             top_left_solution, bottom_right_solution,
                                             search_request,
                                             sampling_method=search_request.sampling_method)
        Sampler.run()

    print('Completed')
