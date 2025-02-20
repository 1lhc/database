from scipy import stats
import numpy as np

def calculate_confidence_interval(data, confidence_level=0.95):
    """
    Calculate the confidence interval for a given dataset.
    :param data: List or array of numerical data points.
    :param confidence_level: Desired confidence level (default is 0.95).
    :return: Tuple (lower_bound, upper_bound) representing the confidence interval.
    """
    if len(data) < 2:
        raise ValueError("At least two data points are required to calculate a confidence interval.")
    mean = np.mean(data)
    sem = stats.sem(data)
    ci = stats.t.interval(confidence_level, len(data)-1, loc=mean, scale=sem)
    return ci