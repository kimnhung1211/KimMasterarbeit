import matplotlib.pyplot as plt
import matplotlib.font_manager
from pathlib import Path


def visualize_front(sampler, current_interval=None, iteration=None):
    plt.clf()

    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.serif'] = 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Ubuntu Mono'
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['xtick.labelsize'] = 8
    plt.rcParams['ytick.labelsize'] = 8
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 12
    plt.xlabel('Travel Time (seconds)')
    plt.ylabel('Price (Euros)')

    if not iteration:
        iteration = 0
    plt.title('Sampling Iteration ' + str(iteration))

    for interval in sampler.intervals_list:
        plt.axvline(x=interval.original_lower_limit,
                    color='grey', linewidth=0.5)
        plt.axvline(x=interval.original_upper_limit,
                    color='grey', linewidth=0.5)

    if current_interval:
        plt.axvline(x=current_interval.original_lower_limit,
                    color='crimson', linewidth=0.8)
        plt.axvline(x=current_interval.original_upper_limit,
                    color='crimson', linewidth=0.8)

    plt.scatter(sampler.top_left_solution.travel_time,
                sampler.top_left_solution.price, zorder=10, color='teal')
    plt.scatter(sampler.bottom_right_solution.travel_time,
                sampler.bottom_right_solution.price, zorder=10, color='teal')

    for interval in sampler.intervals_list:
        if interval.blacklisted:
            plt.axvspan(interval.original_lower_limit,
                        interval.original_upper_limit, facecolor='grey', alpha=0.3)

        if interval.current_solutions:
            for solution in interval.current_solutions:
                plt.scatter(solution.travel_time, solution.price,
                            zorder=10, color='teal')

    Path('./outputpicture/' +
         sampler.search_request.city + "_" + sampler.sampling_method + str(sampler.search_request.number_of_sampling_intervals)).mkdir(parents=True, exist_ok=True)
    plt.savefig('./outputpicture/' + sampler.search_request.city + "_" + sampler.sampling_method + str(sampler.search_request.number_of_sampling_intervals) +
                '/Iteration_' + str(iteration))


def visualize_cummulative_hypervolume(sampler):
    plt.clf()
    plt.xlabel('Iteration')
    plt.ylabel('Cummulative Hypervolume')
    x, y1, y2 = [], [], []
    for index, hv in enumerate(sampler.hypervolume_list):
        x.append(index)
        y1.append(0)
        y2.append(hv)
    plt.plot(x, y2, 'k--')
    plt.fill_between(x, y1, y2, color='#539ecd')
    plt.grid()
    Path('./outputpicture/' +
         sampler.search_request.city + "_" + sampler.sampling_method + str(sampler.search_request.number_of_sampling_intervals)).mkdir(parents=True, exist_ok=True)
    plt.savefig('./outputpicture/' + sampler.search_request.city + "_" + sampler.sampling_method + str(sampler.search_request.number_of_sampling_intervals) + '/cumulative_hypervolume' +
                str(int(sampler.hypervolume_list[-1])))
