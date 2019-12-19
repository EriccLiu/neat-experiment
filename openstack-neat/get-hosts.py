from neat.config import *
import neat.common as common

config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                  REQUIRED_FIELDS)
compute_hosts = common.parse_compute_hosts(config['compute_hosts'])

hosts = ""
for host in compute_hosts:
    hosts += host + " "

print(hosts)