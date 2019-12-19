#!/usr/bin/python2

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

from novaclient import client
import neat.common as common
import neat.globals.manager as manager
from neat.config import *
import re

def vm_hostname(vm):
    return str(getattr(vm, 'OS-EXT-SRV-ATTR:host'))

config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                  REQUIRED_FIELDS)
db = manager.init_db(config['sql_connection'])
nova = client.Client('2.1',
		     config['os_admin_user'],
                     config['os_admin_password'],
                     config['os_admin_tenant_name'],
                     config['os_auth_url'],
                     service_type="compute")
hosts = common.parse_compute_hosts(config['compute_hosts'])

p1 = "192\.168\.1\.1.."
pattern = re.compile(p1)

ips = ""
servers = nova.servers.list()
for server in servers:
    tmp = str(nova.servers.ips(server))
    matcher = re.search(pattern, tmp)
    ips += matcher.group(0) + ' '

print(ips)