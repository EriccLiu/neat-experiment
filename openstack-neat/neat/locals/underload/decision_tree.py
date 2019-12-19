""" decision tree based algorithms.
"""

from contracts import contract
from neat.contracts_primitive import *
from neat.contracts_extra import *

import logging
log = logging.getLogger(__name__)


@contract
def decision_tree_factory(time_step, migration_time, params):
    """ Creates the decision tree algorithm.

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
        decision_tree(params['threshold'],
                     utilization,
                     params['seprate_values']),
                     {})


@contract
def decision_tree(threshold, utilization, seprateValues):
    """ The decision tree based CPU utilization threshold algorithm.

    :param threshold: The default utilization underload threshold.
     :type threshold: float,>=0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: The decision of the algorithm and updated state.
     :rtype: bool
    """

    windowSize = len(seprateValues)
    # history utilization is not sufficient
    if len(utilization) == 0:
        return False
    if len(utilization) < windowSize:
        return utilization[-1] <= threshold
    
    utilization.reverse()
    
    meanReversedUtilization = []
    utilization_sum = 0
    for i in range(windowSize):
         utilization_sum += utilization[i]
         meanReversedUtilization.append(utilization_sum / (i + 1))  

    return HOBDTree(meanReversedUtilization, seprateValues)


def HOBDTree(meanReversedUtilization, seprateValues):
    for i in range(len(seprateValues)):
        if meanReversedUtilization[i] <= seprateValues[i]:
            return True
    return False