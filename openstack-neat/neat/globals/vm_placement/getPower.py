"""get power algorithms
"""
import sys
import math


def getPowerSpec(utilization):
    power = [41.6, 46.7, 52.3, 57.9, 65.4, 73, 80.7, 89.5, 99.6, 105, 113]

    if utilization < 0 or utilization > 1:
        return sys.maxint
    if utilization % 0.1 == 0:
        return power[int(utilization * 10)]
    utilization1 = int(math.floor(utilization * 10))
    utilization2 = int(math.ceil(utilization * 10))
    power1 = power[utilization1]
    power2 = power[utilization2]
    delta = (power2 - power1) / 10
    power = power1 + delta * (utilization - utilization1 / 10.0) * 100
    return power