
# Copyright 2012 Anton Beloglazov
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" The instance state correction module.

Sometimes, the state of some instances would become 'error', however, the instance
is running active.

This module is used to modify nova database to correct these unnormal states.

"""

from contracts import contract
from neat.contracts_primitive import *
from neat.contracts_extra import *

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

import novaclient
from novaclient import client
import time

import neat.common as common
from neat.config import *

import logging
log = logging.getLogger(__name__)

@contract
def start():
    """ Start the local manager loop.

    :return: The final state.
     :rtype: dict(str: *)
    """

def start():
    """ Start the global manager web service.
    """
    config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                      REQUIRED_FIELDS)

    common.init_logging(
        config['log_directory'],
        'vm-state-corrector.log',
        int(config['log_level']))
    interval = int(config['local_manager_interval']) / 5
    
    if log.isEnabledFor(logging.INFO):
        log.info('Starting the vm state corrector, ' +
                 'iterations every %s seconds', interval)
    
    state = init_state(config)

    return common.start(
        init_state,
        execute,
        config,
        int(interval))


@contract
def init_state(config):
    """ Initialize a dict for storing the state of the global manager.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :return: A dict containing the initial state of the global managerr.
     :rtype: dict
    """

    engine = create_engine("mysql://nova:stack@controller/nova")  # 'sqlite:///:memory:'
    Session = sessionmaker(bind=engine)
    session = Session()

    return {'session': session,
            'nova': client.Client('2.1',
				  config['os_admin_user'],
                  config['os_admin_password'],
                  config['os_admin_tenant_name'],
                  config['os_auth_url'],
                  service_type="compute")}


@contract
def execute(config, state):
    """ Execute an iteration of the local manager.

    Find instances whose states are not 'active'
    
    Modify these states to 'active'

    :param config: A config dictionary.
     :type config: dict(str: *)

    :param state: A state dictionary.
     :type state: dict(str: *)

    :return: The updated state dictionary.
     :rtype: dict(str: *)
    """
    log.info('Started an iteration')

    nova = state['nova']
    session = state['session']

    all_vms = nova.servers.list()
    active_vms = nova.servers.list(search_opts={'status':'ACTIVE'})
    migrating_vms = nova.servers.list(search_opts={'status':'MIGRATING'})
    unexpected_vms = [ i for i in all_vms if (i not in active_vms) and (i not in migrating_vms)]

    if log.isEnabledFor(logging.INFO):
            log.info("Unexpected instances: %s", unexpected_vms)

    for vm in unexpected_vms:
        sql = "update instances set vm_state = 'active' where uuid = '" + str(vm.id) + "'"
        if log.isEnabledFor(logging.INFO):
            log.info(sql)
        
        session.execute(sql)
        session.commit()

    if log.isEnabledFor(logging.INFO):
        log.info('Completed an iteration')

    return state

if __name__ == "__main__":
    start()
