from hv import HyperVolume
from config import hv_normalization_factor
import itertools


def calculate_hv(intervals_list, hv_reference_point):
    referencePoint = hv_reference_point
    hyperVolume = HyperVolume(referencePoint)

    front = []
    for interval in intervals_list:
        for solution in interval.current_solutions:
            front.append(
                [solution.travel_time/hv_normalization_factor, solution.price])
    front.sort()
    front = list(front for front, _ in itertools.groupby(front))
    result = hyperVolume.compute(front)
    return result
