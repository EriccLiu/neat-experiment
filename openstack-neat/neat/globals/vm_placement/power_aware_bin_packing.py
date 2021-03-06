""" Power Aware Best Fit Decreasing based VM placement algorithms.
"""

import sys
from contracts import contract
from neat.contracts_primitive import *
from neat.contracts_extra import *
import getPower as gp

import logging
log = logging.getLogger(__name__)


@contract
def power_aware_best_fit_decreasing_factory(time_step, migration_time, params):
    """ Creates the Best Fit Decreasing (BFD) heuristic for VM placement.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: float,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the BFD algorithm.
     :rtype: function
    """
    return lambda hosts_cpu_usage, hosts_cpu_total, \
                  hosts_ram_usage, hosts_ram_total, \
                  inactive_hosts_cpu, inactive_hosts_ram, \
                  vms_cpu, vms_ram, state=None: \
        (power_aware_best_fit_decreasing(
            params['last_n_vm_cpu'],
            get_available_resources(
                    params['cpu_threshold'],
                    hosts_cpu_usage,
                    hosts_cpu_total),
            get_available_resources(
                    params['ram_threshold'],
                    hosts_ram_usage,
                    hosts_ram_total),
            inactive_hosts_cpu,
            inactive_hosts_ram,
            hosts_cpu_usage, 
            hosts_cpu_total,
            hosts_ram_usage, 
            hosts_ram_total,
            vms_cpu,
            vms_ram,
            params['getPower']),
         {})


@contract
def get_available_resources(threshold, usage, total):
    """ Get a map of the available resource capacity.

    :param threshold: A threshold on the maximum allowed resource usage.
     :type threshold: float,>=0

    :param usage: A map of hosts to the resource usage.
     :type usage: dict(str: number)

    :param total: A map of hosts to the total resource capacity.
     :type total: dict(str: number)

    :return: A map of hosts to the available resource capacity.
     :rtype: dict(str: int)
    """
    return dict((host, int(threshold * total[host] - resource))
                for host, resource in usage.items())

def getPower(param, utilization):
    if param == 'spec':
        return int(gp.getPowerSpec(utilization))
    else:
        return sys.maxint

@contract
def power_aware_best_fit_decreasing(last_n_vm_cpu, hosts_cpu, hosts_ram,
                        inactive_hosts_cpu, inactive_hosts_ram,
                        hosts_cpu_usage, hosts_cpu_total, 
                        hosts_ram_usage, hosts_ram_total, 
                        vms_cpu, vms_ram, getPowerParam):
    """ The Best Fit Decreasing (BFD) heuristic for placing VMs on hosts.

    :param last_n_vm_cpu: The last n VM CPU usage values to average.
     :type last_n_vm_cpu: int

    :param hosts_cpu: A map of host names and their available CPU in MHz.
     :type hosts_cpu: dict(str: int)

    :param hosts_ram: A map of host names and their available RAM in MB.
     :type hosts_ram: dict(str: int)

    :param inactive_hosts_cpu: A map of inactive hosts and available CPU MHz.
     :type inactive_hosts_cpu: dict(str: int)

    :param inactive_hosts_ram: A map of inactive hosts and available RAM MB.
     :type inactive_hosts_ram: dict(str: int)

    :param vms_cpu: A map of VM UUID and their CPU utilization in MHz.
     :type vms_cpu: dict(str: list(int))

    :param vms_ram: A map of VM UUID and their RAM usage in MB.
     :type vms_ram: dict(str: int)

    :return: A map of VM UUIDs to host names, or {} if cannot be solved.
     :rtype: dict(str: str)
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug('last_n_vm_cpu: %s', str(last_n_vm_cpu))
        log.debug('hosts_cpu: %s', str(hosts_cpu))
        log.debug('hosts_ram: %s', str(hosts_ram))
        log.debug('hosts_cpu_usage: %s', str(hosts_cpu_usage))
        log.debug('hosts_ram_usage: %s', str(hosts_ram_usage))
        log.debug('hosts_cpu_total: %s', str(hosts_cpu_total))
        log.debug('hosts_ram_total: %s', str(hosts_ram_total))
        log.debug('inactive_hosts_cpu: %s', str(inactive_hosts_cpu))
        log.debug('inactive_hosts_ram: %s', str(inactive_hosts_ram))
        log.debug('vms_cpu: %s', str(vms_cpu))
        log.debug('vms_ram: %s', str(vms_ram))
    vms_tmp = []
    for vm, cpu in vms_cpu.items():
        if cpu:
            last_n_cpu = cpu[-last_n_vm_cpu:]
            vms_tmp.append((sum(last_n_cpu) / len(last_n_cpu),
                            vms_ram[vm],
                            vm))
        else:
            log.warning('No CPU data for VM: %s - skipping', vm)

    vms = sorted(vms_tmp, reverse=True)
    hosts = sorted(((v, hosts_ram[k], k)
                    for k, v in hosts_cpu.items()))
    inactive_hosts = sorted(((v, inactive_hosts_ram[k], k)
                             for k, v in inactive_hosts_cpu.items()))
    mapping = {}
    for vm_cpu, vm_ram, vm_uuid in vms:
        min = sys.maxint
        mapped = False
        while not mapped:
            for _, _, host in hosts:
                if hosts_cpu[host] >= vm_cpu and \
                    hosts_ram[host] >= vm_ram:
                        power = getPower(getPowerParam, float(hosts_cpu_usage[host]) / hosts_cpu_total[host])
                        log.debug("host("+str(host)+") power: " + str(power))
                        if power < min:
                            mapping[vm_uuid] = host
                            min = power
                            mapped = True
            else:
                if mapped:
                    hosts_cpu[host] -= vm_cpu
                    hosts_ram[host] -= vm_ram
                    hosts_cpu_usage[host] += vm_cpu
                    hosts_ram_usage[host] += vm_ram
                    break
                if inactive_hosts:
                    activated_host = inactive_hosts.pop(0)
                    hosts.append(activated_host)
                    hosts = sorted(hosts)
                    hosts_cpu[activated_host[2]] = activated_host[0]
                    hosts_ram[activated_host[2]] = activated_host[1]
                    hosts_cpu_usage[activated_host[2]] = 0
                    hosts_ram_usage[activated_host[2]] = 0
                else:
                    break
    if len(vms) == len(mapping):
        return mapping
    return {}