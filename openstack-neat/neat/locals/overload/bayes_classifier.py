""" bayes_classifier based algorithms.
"""

from contracts import contract
from neat.contracts_primitive import *
from neat.contracts_extra import *

import logging
log = logging.getLogger(__name__)


@contract
def bayes_classifier_factory(time_step, migration_time, params):
    """ Creates the bayes_classifier algorithm.

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
        bayes_classifier(params['threshold'],
                     utilization,
                     params['seprate_values']),
                     {})


@contract
def bayes_classifier(threshold, utilization, seprateValues):
    """ The bayes_classifier based CPU utilization threshold algorithm.

    :param threshold: The default utilization overload threshold.
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
        return utilization[-1] >= threshold
    
    utilization.reverse()
    
    meanReversedUtilization = []
    utilization_sum = 0
    for i in range(windowSize):
         utilization_sum += utilization[i]
         meanReversedUtilization.append(utilization_sum / (i + 1))  

    loadState = getLoadState(meanReversedUtilization, seprateValues)

    return HSNBC(loadState)


def getLoadState(meanReversedUtilization, seprateValues):
    loadState = []
    for i in range(len(seprateValues)):
        if meanReversedUtilization[i] >= seprateValues[i]:
            loadState.append(True)
        else:
            loadState.append(False)
    return loadState


def HSNBC(loadState):
    # defin priori and conditional probability, 0(not overload) and 1(overload)
    priori = [0.990458, 0.009542]
    cp = [[0.000357, 0.000168, 0.000276, 0.000406, 0.000992,
           0.001073, 0.001136, 0.001222, 0.001292, 0.001363], 
          [0.642226, 0.097315, 0.187919, 0.267617, 0.491331, 
           0.509228, 0.524049, 0.546421, 0.577181, 0.619407]]

    p0 = priori[0]
    p1 = priori[1]
    for i in range(len(loadState)):
        if loadState[i]:
            p0 *= cp[0][i]
            p1 *= cp[1][i]
        else:
            p0 *= 1 - cp[0][i]
            p1 *= 1 - cp[1][i]
    
    return True if p1 > p0 else False