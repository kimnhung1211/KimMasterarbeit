import helper

def create_output_dict(G, path):
    price = helper.path_length(G, path, 'price')
    travel_time = helper.path_length(G, path, 'travel_time')
    number_of_transfer = helper.path_length(G, path, 'number_of_transfer')