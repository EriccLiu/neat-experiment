from contracts import contract
from neat.contracts_primitive import *
from neat.contracts_extra import *

import requests
requests.adapters.DEFAULT_RETRIES = 10
from hashlib import sha1
import time

import neat.common as common
from neat.config import *
from neat.db_utils import *

import logging
log = logging.getLogger(__name__)

@contract
def overload_detection():
    """ decide whether the host is overload, and write the decision in a file.
    
    :return: overload decision.
     :rtype: dict(str: *)
    """
    config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                      REQUIRED_FIELDS)

    state = init_state(config)

    vm_path = common.build_local_vm_path(config['local_data_directory'])
    vm_cpu_mhz = get_local_vm_data(vm_path)
    vm_ram = get_ram(state['vir_connection'], vm_cpu_mhz.keys())
    vm_cpu_mhz = cleanup_vm_data(vm_cpu_mhz, vm_ram.keys())

    host_path = common.build_local_host_path(config['local_data_directory'])
    host_cpu_mhz = get_local_host_data(host_path)

    overload_detection_params = common.parse_parameters(
        config['algorithm_overload_detection_parameters'])
    
    overload_detection = common.call_function_by_name(
        config['algorithm_overload_detection_factory'],
        [0,
        0,
        overload_detection_params])

    host_cpu_utilization = vm_mhz_to_percentage(
        vm_cpu_mhz.values(),
        host_cpu_mhz,
        state['physical_cpu_mhz_total'])

    state['overload_detection'] = overload_detection
    state['overload_detection_state'] = {}

    overload, state['overload_detection_state'] = overload_detection(
        host_cpu_utilization, state['overload_detection_state'])

    return 1 if overload else 0

@contract
def underload_detection():
    """ decide whether the host is underload, and write the decision in a file.
    
    :return: underload decision.
     :rtype: dict(str: *)
    """
    config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                     REQUIRED_FIELDS)

    state = init_state(config)

    vm_path = common.build_local_vm_path(config['local_data_directory'])
    vm_cpu_mhz = get_local_vm_data(vm_path)
    vm_ram = get_ram(state['vir_connection'], vm_cpu_mhz.keys())
    vm_cpu_mhz = cleanup_vm_data(vm_cpu_mhz, vm_ram.keys())

    host_path = common.build_local_host_path(config['local_data_directory'])
    host_cpu_mhz = get_local_host_data(host_path)

    underload_detection_params = common.parse_parameters(
        config['algorithm_underload_detection_parameters'])
    
    underload_detection = common.call_function_by_name(
        config['algorithm_underload_detection_factory'],
        [0,
        0,
        underload_detection_params])
    state['underload_detection'] = underload_detection
    state['underload_detection_state'] = {}

    host_cpu_utilization = vm_mhz_to_percentage(
        vm_cpu_mhz.values(),
        host_cpu_mhz,
        state['physical_cpu_mhz_total'])

    underload, state['underload_detection_state'] = underload_detection(
        host_cpu_utilization, state['underload_detection_state'])

    return 1 if underload else 0

@contract
def init_state(config):
    """ Initialize a dict for storing the state of the local manager.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :return: A dictionary containing the initial state of the local manager.
     :rtype: dict
    """
    vir_connection = libvirt.openReadOnly(None)
    if vir_connection is None:
        print 'Failed to open a connection to the hypervisor'
        raise OSError(message)

    physical_cpu_mhz_total = int(
        common.physical_cpu_mhz_total(vir_connection) *
        float(config['host_cpu_usable_by_vms']))
    return {'vir_connection': vir_connection,
            'physical_cpu_mhz_total': physical_cpu_mhz_total}

@contract
def vm_mhz_to_percentage(vm_mhz_history, host_mhz_history, physical_cpu_mhz):
    """ Convert VM CPU utilization to the host's CPU utilization.

    :param vm_mhz_history: A list of CPU utilization histories of VMs in MHz.
     :type vm_mhz_history: list(list(int))

    :param host_mhz_history: A history if the CPU usage by the host in MHz.
     :type host_mhz_history: list(int)

    :param physical_cpu_mhz: The total frequency of the physical CPU in MHz.
     :type physical_cpu_mhz: int,>0

    :return: The history of the host's CPU utilization in percentages.
     :rtype: list(float)
    """
    max_len = max(len(x) for x in vm_mhz_history)
    if len(host_mhz_history) > max_len:
        host_mhz_history = host_mhz_history[-max_len:]
    mhz_history = [[0] * (max_len - len(x)) + x
                   for x in vm_mhz_history + [host_mhz_history]]
    return [float(sum(x)) / physical_cpu_mhz for x in zip(*mhz_history)]

@contract
def get_local_vm_data(path):
    """ Read the data about VMs from the local storage.

    :param path: A path to read VM UUIDs from.
     :type path: str

    :return: A map of VM UUIDs onto the corresponing CPU MHz values.
     :rtype: dict(str : list(int))
    """
    result = {}
    for uuid in os.listdir(path):
        with open(os.path.join(path, uuid), 'r') as f:
            result[uuid] = [int(x) for x in f.read().strip().splitlines()]
    return result

@contract
def get_local_host_data(path):
    """ Read the data about the host from the local storage.

    :param path: A path to read the host data from.
     :type path: str

    :return: A history of the host CPU usage in MHz.
     :rtype: list(int)
    """
    if not os.access(path, os.F_OK):
        return []
    with open(path, 'r') as f:
        result = [int(x) for x in f.read().strip().splitlines()]
    return result


@contract
def cleanup_vm_data(vm_data, uuids):
    """ Remove records for the VMs that are not in the list of UUIDs.

    :param vm_data: A map of VM UUIDs to some data.
     :type vm_data: dict(str: *)

    :param uuids: A list of VM UUIDs.
     :type uuids: list(str)

    :return: The cleaned up map of VM UUIDs to data.
     :rtype: dict(str: *)
    """
    for uuid, _ in vm_data.items():
        if uuid not in uuids:
            del vm_data[uuid]
    return vm_data


@contract
def get_ram(vir_connection, vms):
    """ Get the maximum RAM for a set of VM UUIDs.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :param vms: A list of VM UUIDs.
     :type vms: list(str)

    :return: The maximum RAM for the VM UUIDs.
     :rtype: dict(str : long)
    """
    vms_ram = {}
    for uuid in vms:
        ram = int(get_max_ram(vir_connection, uuid))
        if ram:
            vms_ram[uuid] = ram

    return vms_ram


@contract
def get_max_ram(vir_connection, uuid):
    """ Get the max RAM allocated to a VM UUID using libvirt.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :param uuid: The UUID of a VM.
     :type uuid: str[36]

    :return: The maximum RAM of the VM in MB.
     :rtype: long|None
    """
    try:
        domain = vir_connection.lookupByUUIDString(uuid)
        return domain.maxMemory() / 1024
    except libvirt.libvirtError:
        return None

if __name__ == "__main__":
    overload = overload_detection()
    underload = underload_detection()
    print(str(overload) + "," + str(underload))