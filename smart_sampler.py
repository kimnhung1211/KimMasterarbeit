import config
import pylgrim
import random
import numpy as np
from operator import attrgetter
from utils import helper
import entites
import visualization
from hv import HyperVolume
from config import hv_normalization_factor
import itertools
import timeit


class SmartSampler(object):

    def __init__(self, intervals_list, G, res_name,
                 source, target, hv_reference_point,
                 top_left_solution, bottom_right_solution, search_request,
                 sampling_method):
        self.intervals_list = intervals_list
        self.G = G
        self.res_name = res_name
        self.source = source
        self.target = target
        self.hv_reference_point = hv_reference_point
        self.top_left_solution = top_left_solution
        self.bottom_right_solution = bottom_right_solution
        self.search_request = search_request
        self.sampling_method = sampling_method
        self.update_interval_scores()
        self.G_pre, self.res_min = self.preprocess_graph()
        self.hypervolume_list = []
        visualization.visualize_front(self)
        self.hypervolume_list.append(self.calculate_current_hypervolume())
        print("Done setting up Sampler!")

    def calculate_current_hypervolume(self):
        referencePoint = self.hv_reference_point
        hyperVolume = HyperVolume(referencePoint)

        front = []
        front.append([self.top_left_solution.travel_time /
                      hv_normalization_factor, self.top_left_solution.price])
        front.append([self.bottom_right_solution.travel_time /
                      hv_normalization_factor, self.bottom_right_solution.price])

        for interval in self.intervals_list:
            for solution in interval.current_solutions:
                front.append(
                    [solution.travel_time/hv_normalization_factor, solution.price])
        front.sort()
        front = list(front for front, _ in itertools.groupby(front))
        result = hyperVolume.compute(front)
        return result

    def update_interval_scores(self):
        all_solutions = [item for sublist in
                         [interval.current_solutions
                          for interval in self.intervals_list]
                         for item in sublist]
        all_solutions.extend(
            [self.top_left_solution, self.bottom_right_solution])
        all_solutions.sort(key=lambda x: x.travel_time, reverse=False)
        for interval in self.intervals_list:
            left_solution = [
                s for s in all_solutions if s.travel_time
                <= interval.original_lower_limit][-1]
            if interval.current_solutions:
                right_solution = interval.current_solutions[-1]
            else:
                try:
                    right_solution = [
                        s for s in all_solutions if
                        s.travel_time >= interval.original_upper_limit][0]
                except IndexError:
                    right_solution = all_solutions[-1]

            interval.score = (left_solution.price - right_solution.price) / \
                ((right_solution.travel_time - left_solution.travel_time) /
                 config.hv_normalization_factor)
        print("Done Updating Interval Scores!")

    def preprocess_graph(self):
        highest_interval_upper = self.intervals_list[-1].upper_limit
        G_pre, res_min = pylgrim.ESPPRC.preprocess(self.G, self.source, self.target,
                                                   list(
                                                       [highest_interval_upper]),
                                                   res_name=self.res_name)
        print("Graph Pre-Processing Finished!")
        return G_pre, res_min

    def select_interval(self, i):
        if self.sampling_method == 'systemic':
            return self.intervals_list[i-1]
        else:
            not_black_listed_intervals = [
                interval for interval in self.intervals_list
                if interval.blacklisted == False]
            random.shuffle(not_black_listed_intervals)
            if not_black_listed_intervals:
                p = np.random.rand()
                if p < config.epsilon:
                    selected_interval = random.choice(
                        not_black_listed_intervals)
                else:
                    selected_interval = max(
                        not_black_listed_intervals, key=attrgetter('score'))
                return selected_interval
            else:
                return None

    def run(self):
        i = 0
        start_time = timeit.default_timer()
        while i < self.search_request.number_of_sampling_intervals:
            i += 1
            selected_interval = self.select_interval(i)
            if selected_interval:
                solution = self.sample(selected_interval)
                if solution:
                    print("Sample point " + str(i))

                    print("Travel Time: " + str(solution.travel_time))

                    print("Price: " + str(solution.price))
                    self.update_interval(selected_interval, solution)
                else:
                    print("No Solution Found!")
            else:
                break
            self.update_interval_scores()
            visualization.visualize_front(self, selected_interval, i)
            self.hypervolume_list.append(self.calculate_current_hypervolume())
        visualization.visualize_cummulative_hypervolume(self)
        elapsed = timeit.default_timer() - start_time
        self.write_soution_info(elapsed)
        print("Total Sampling Time For " + self.sampling_method +
              " " + str(elapsed) + " seconds")
        print("Finished Sampling")

    def write_soution_info(self, elapsed):
        filename = './outputpicture/' + self.search_request.city + "_" + \
            self.sampling_method + \
            str(self.search_request.number_of_sampling_intervals)
        with open(filename + '/solinfo.csv', 'w+') as file:
            file.write("TOTAL RUNTIME: " +
                       str(elapsed))
            file.write('\n')

            file.write("Sample method: " +
                       self.sampling_method)
            file.write('\n')

            file.write("Datetime: " +
                       str(self.search_request.earliest_departure))
            file.write('\n')
            file.write(str(self.search_request.departure_lat) +
                       str(self.search_request.departure_lon) +
                       str(self.search_request.arrival_lat) +
                       str(self.search_request.arrival_lon))
            file.write('\n')
            for index, hv in enumerate(self.hypervolume_list):
                file.write("HV " +
                           str(index) + ": " + str(hv))
                file.write('\n')
            solutions_set = self.solutions_set()
            for index, sol in enumerate(solutions_set):
                file.write("SOL " +
                           str(index) + ": travel time " + str(sol.travel_time)
                           + " price " + str(sol.price))
                file.write('\n')

    def sample(self, selected_interval):
        max_res = list([selected_interval.upper_limit])
        print("\n\n...Sampling " + selected_interval.__repr__())
        best_path, best_path_label = pylgrim.ESPPRC.GSSA(self.G_pre, self.source,
                                                         self.target, max_res,
                                                         self.res_min,
                                                         res_name=self.res_name)
        if best_path:
            path_nodes = list(best_path.nodes._nodes.keys())

            travel_time = helper.path_length(self.G,
                                             path_nodes,
                                             config.secondary_objective_name)[0]
            price = helper.path_length(self.G,
                                       path_nodes,
                                       config.primary_objective_name)

            solution = entites.Solution(travel_time, price, path_nodes)

            return solution
        else:
            return None

    def update_interval(self, selected_interval, solution):
        wrong_interval = selected_interval.update_interval(
            solution, current_interval=True)
        if wrong_interval:
            try:
                correct_interval = [interval for interval in
                                    self.intervals_list if
                                    solution.travel_time >=
                                    interval.lower_limit and
                                    solution.travel_time
                                    <= interval.upper_limit+1][0]
                correct_interval.update_interval(
                    solution, current_interval=False)

                intervals_in_between = \
                    [interval for interval in
                     self.intervals_list if (interval.original_lower_limit
                                             >= min([i.original_upper_limit for i in [
                                                 selected_interval, correct_interval]])
                                             and interval.original_upper_limit
                                             <= max([i.original_lower_limit for i in [
                                                 selected_interval, correct_interval]]))]
                if intervals_in_between:
                    for i in intervals_in_between:
                        i.blacklisted = True
            except IndexError:
                pass

    def solutions_set(self):
        all_solutions = [item for sublist in
                         [interval.current_solutions
                          for interval in self.intervals_list]
                         for item in sublist]
        all_solutions.extend(
            [self.top_left_solution, self.bottom_right_solution])
        all_solutions.sort(key=lambda x: x.travel_time, reverse=False)
        return all_solutions
