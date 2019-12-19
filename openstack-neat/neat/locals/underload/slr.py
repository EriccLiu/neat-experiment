""" roubust simple linear regression based algorithms.
"""

from contracts import contract
from neat.contracts_primitive import *
from neat.contracts_extra import *

import logging
log = logging.getLogger(__name__)


@contract
def slr_factory(time_step, migration_time, params):
    """ Creates the simple linear regression algorithm.

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
        simple_linear_regression(params['metric'].lower(),
                                 params['threshold'],
                                 params['n'],
                                 utilization,
                                 params['path']+'host_prediction',
                                 params['path']+'host_x'),
                             {})


@contract
def simple_linear_regression(matric, threshold, n, utilization, prediction_path, x_path):
    """ The SLR based CPU utilization threshold algorithm.

    :param matric: The threshold on the OTF value.
     :type matric: str

    :param threshold: The utilization overload threshold.
     :type threshold: float,>=0

    :param n: The number of last CPU utilization values to average.
     :type n: int,>0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :param prediction_path: The path to save history prediction CPU utilization.
     :type prediction_path: str

    :param x_path: The path to save history x value for linear regression function.
     :type x_path: str

    :return: The decision of the algorithm and updated state.
     :rtype: bool
    """
    # 读取真实与预测的utilization
    # 截取长度：n，不足用0补
    predicted_utilization = []
    x_utilization = []
    if not os.access(prediction_path, os.F_OK):
        predicted_utilization.append(0)
    else:
        with open(prediction_path, 'r') as f:
            for line in f.readlines():
                predicted_utilization.append(float(line))
    
    if not os.access(x_path, os.F_OK):
        with open(x_path, 'w') as f:
            f.write(str(1) + '\n')
        x_utilization.append(1)        
    else:
        with open(x_path, 'r') as f:
            for line in f.readlines():
                x_utilization.append(float(line))

    actual_utilization = utilization[-n:]
    x_current = x_utilization[-1] + 1

    # 计算统计量
    xMean, actualMean, b0, b1 = calculateStatistics(x_utilization, actual_utilization)

    # 计算误差error
    if matric == 'mse':
        error = mse(actual_utilization, predicted_utilization)
        prediction = b0 + b1 * x_current + error
    elif matric == 'rmse':
        error = rmse(actual_utilization, predicted_utilization)
        prediction = b0 + b1 * x_current + error
    elif matric == 'mae':
        error = mae(actual_utilization, predicted_utilization)
        prediction = b0 + b1 * x_current + error
    elif matric == 'ewmae':
        error = ewmae(actual_utilization, predicted_utilization)
        prediction = b0 + b1 * x_current + error
    elif matric == 'se':
        error = se(actual_utilization, x_utilization, predicted_utilization)
        prediction = b0 + (b1 + error) * x_current
    #elif matric == 'cislope':
    #    error = cislop0.3e(actual_utilization, x_utilization, predicted_utilization)
    else:
        return False

    prediction = max(0, prediction)
    prediction = min(1, prediction)

    # 记录预测值
    append_prediction_data_locally(prediction_path, prediction, n)
    append_x_locally(x_path, n)

    return prediction <= threshold


def calculateStatistics(x_utilization, y_utilization):
    """ The function to calculate basic statistics.

    :param x_utilization: The history of the host's x values.
     :type x_utilization: list(float)

    :param predicted_utilization: The history of the host's CPU predicted utilization.
     :type predicted_utilization: list(float)
    
    :param n: The number of last CPU utilization values to average.
     :type n: int,>0
    
    :return: mean values of x and predicted utilization and b0, b1 for linear regression funciton.
     :rtype: float, float, float, float
    """
    windowSize = len(x_utilization)

    xMean = sum(x_utilization) / windowSize
    yMean = sum(y_utilization) / windowSize

    # 计算b1
    b1 = 0
    tmp = 0
    for i in range(windowSize):
        b1 += (x_utilization[i] - xMean) * (y_utilization[i] - yMean)
        tmp += (x_utilization[i] - xMean) ** 2

    if tmp == 0:
        b1 = 0
    else:
        b1 /= tmp
    # 计算b0
    b0 = yMean - b1 * xMean
    
    return xMean, yMean, b0, b1

def mse(actual_utilization, predicted_utilization):
    """ The function to calculate MSE.

    :param actual_utilization: The history of the host's CPU actual utilization.
     :type actual_utilization: list(float)

    :param predicted_utilization: The history of the host's CPU predicted utilization.
     :type predicted_utilization: list(float)
    
    :return: error of MSE metric.
     :rtype: float
    """
    error = 0
    windowSize = len(actual_utilization)
    if windowSize <= 2:
        return None

    for i in range(windowSize):
        error += (actual_utilization[i] - predicted_utilization[i]) ** 2
    error /= (windowSize - 2)
    return error

def rmse(actual_utilization, predicted_utilization):
    """ The function to calculate RMSE.

    :param actual_utilization: The history of the host's CPU actual utilization.
     :type actual_utilization: list(float)

    :param predicted_utilization: The history of the host's CPU predicted utilization.
     :type predicted_utilization: list(float)
    
    :return: error of RMSE metric.
     :rtype: float
    """
    error = mse(actual_utilization, predicted_utilization)
    error **= 0.5
    return error

def mae(actual_utilization, predicted_utilization):
    """ The function to calculate MAE.

    :param actual_utilization: The history of the host's CPU actual utilization.
     :type actual_utilization: list(float)

    :param predicted_utilization: The history of the host's CPU predicted utilization.
     :type predicted_utilization: list(float)
    
    :return: error of MAE metric.
     :rtype: float
    """
    error = 0
    windowSize = len(actual_utilization)

    if windowSize <= 0:
        return None

    for i in range(windowSize):
        error += abs(actual_utilization[i] - predicted_utilization[i])
    error /= windowSize
    return error

def ewmae(actual_utilization, predicted_utilization):
    """ The function to calculate EWMAE.

    :param actual_utilization: The history of the host's CPU actual utilization.
     :type actual_utilization: list(float)

    :param predicted_utilization: The history of the host's CPU predicted utilization.
     :type predicted_utilization: list(float)
    
    :return: error of EWMAE metric.
     :rtype: float
    """
    error = 0
    windowSize = len(actual_utilization)
        
    if windowSize == 3:
        error += 0.2 * abs(actual_utilization[-3] - predicted_utilization[-3])
        error += 0.3 * abs(actual_utilization[-2] - predicted_utilization[-2])
        error += 0.5 * abs(actual_utilization[-1] - predicted_utilization[-1])
    elif windowSize == 10:
        error += 0.06 * abs(actual_utilization[-10] - predicted_utilization[-10])
        for i in range(2):
            error += 0.07 * abs(actual_utilization[-9+i] - predicted_utilization[-9+i])
        for i in range(4):
            error += 0.08 * abs(yActactual_utilizationual[-7+i] - predicted_utilization[-7+i])
        error += 0.12 * abs(actual_utilization[-3] - predicted_utilization[-3])
        error += 0.16 * abs(actual_utilization[-2] - predicted_utilization[-2])
        error += 0.2 * abs(actual_utilization[-1] - predicted_utilization[-1])
    else:
        return None

    return error

def se(actual_utilization, x_utilization, predicted_utilization):
    """ The function to calculate SE.

    :param actual_utilization: The history of the host's CPU actual utilization.
     :type actual_utilization: list(float)

    :param x_utilization: The history of x utilization.
     :type x_utilization: list(float)
    
    :param predicted_utilization: The history of the host's CPU predicted utilization.
     :type predicted_utilization: list(float)
    
    :return: error of SE metric.
     :rtype: float
    """
    error = rmse(actual_utilization, predicted_utilization)
    windowSize = len(actual_utilization)

    tmp = 0
    x_mean = 0
    # 计算平均值
    for i in range(windowSize):
        x_mean += x_utilization[i]
    x_mean /= windowSize
    # 算分母
    for i in range(windowSize):
        tmp += (x_utilization[i] - x_mean) ** 2
    tmp **= 0.5
    # 算最终的se(b1)误差 
    error /= tmp
    return error

def append_prediction_data_locally(path, data, data_length):
    """ Write a predicted CPU MHz value for the host.

    :param path: A path to write the data to.
     :type path: str

    :param cpu_mhz: A CPU MHz value.
     :type cpu_mhz: int,>=0

    :param data_length: The maximum allowed length of the data.
     :type data_length: int
    """
    if not os.access(path, os.F_OK):
        with open(path, 'w') as f:
            f.write(str(0) + '\n')
            f.write(str(data) + '\n')
    else:
        with open(path, 'r+') as f:
            values = deque(f.read().strip().splitlines(), data_length)
            values.append(data)
            f.truncate(0)
            f.seek(0)
            f.write('\n'.join([str(x) for x in values]) + '\n')

def append_x_locally(path, data_length):
    """ Write next x value for the host.

    :param path: A path to write the data to.
     :type path: str

    :param data_length: The maximum allowed length of the data.
     :type data_length: int
    """
    if not os.access(path, os.F_OK):
        with open(path, 'w') as f:
            f.write(str(1) + '\n')
    else:
        with open(path, 'r+') as f:
            values = deque(f.read().strip().splitlines(), data_length)
            values.append(int(values[-1]) + 1)
            f.truncate(0)
            f.seek(0)
            f.write('\n'.join([str(x) for x in values]) + '\n')