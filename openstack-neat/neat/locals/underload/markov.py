""" markov based algorithms.
"""

from contracts import contract
from neat.contracts_primitive import *
from neat.contracts_extra import *

import logging
log = logging.getLogger(__name__)


@contract
def markov_factory(time_step, migration_time, params):
    """ Creates the markov algorithm.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: float,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the SLR algorithm.
     :rtype: function
    """
    return lambda utilization, state=None: (
        markov(params['threshold'],
                     utilization,
                     params['limit'],
                     params['order']),
                     {})


@contract
def markov(threshold, utilization, limit, order):
    """ The markov based CPU utilization threshold algorithm.

    :param threshold: The default utilization underload threshold.
     :type threshold: float,>=0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: The decision of the algorithm and updated state.
     :rtype: bool
    """
    # 3-order Markov Chain Transition Matrix
    R = [[0.965165, 0.034299, 0.000536], [0.729800, 0.267658, 0.002541], 
        [0.644444, 0.195556, 0.160000], [0.758803, 0.238561, 0.002637],
        [0.455833, 0.539722, 0.004444], [0.463415, 0.426829, 0.109756],
        [0.705882, 0.156863, 0.137255], [0.464286, 0.404762, 0.130952],
        [0.297297, 0.216216, 0.486486], [0.746724, 0.250447, 0.002829],
        [0.461057, 0.534028, 0.004914], [0.388235, 0.364706, 0.247059],
        [0.497861, 0.497308, 0.004831], [0.132676, 0.848201, 0.019123],
        [0.050378, 0.648615, 0.301008], [0.541176, 0.270588, 0.188235],
        [0.055631, 0.704206, 0.240163], [0.032110, 0.442661, 0.525229],
        [0.680180, 0.180180, 0.139640], [0.357143, 0.442857, 0.200000],
        [0.304348, 0.108696, 0.586957], [0.451613, 0.376344, 0.172043],
        [0.050697, 0.697085, 0.252218], [0.020619, 0.481959, 0.497423],
        [0.336842, 0.157895, 0.505263], [0.029083, 0.527964, 0.442953],
        [0.066934, 0.310576, 0.622490]]

    # history utilization is not sufficient
    if len(utilization) == 0:
        return False

    if len(utilization) < order:
        return utilization[-1] <= threshold

    # calculate step threshold
    if len(utilization) < limit:
        Tu = 0.90
        Tl = 0.17
    else:
        Tu = 1 - 1.5 * iqr(utilization)
        Tl = 0.25 * Tu
    
    X = utilization[-order:]
    Y = []
    # 0-underload, 1-normal, 2-overload
    for i in range(order):
        if X[i] <= Tl:
            Y.append(0)
        elif X[i] >= Tu:
            Y.append(2)
        else:
            Y.append(1)

    q1 = R[Y[0] * 9 + Y[1] * 3 + Y[2]][0]
    q2 = R[Y[0] * 9 + Y[1] * 3 + Y[2]][1]
    q3 = R[Y[0] * 9 + Y[1] * 3 + Y[2]][2]

    if q1 > q2 and q1 > q3:
        return True
    else:
        return False


@contract
def iqr(data):
    """ Calculate the Interquartile Range from the data.

    :param data: The data to analyze.
     :type data: list(number)

    :return: The calculated IQR.
     :rtype: float
    """
    sorted_data = sorted(data)
    n = len(data) + 1
    q1 = int(round(0.25 * n)) - 1
    q3 = int(round(0.75 * n)) - 1
    return float(sorted_data[q3] - sorted_data[q1])
