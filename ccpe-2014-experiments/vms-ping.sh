#!/bin/sh

for ip in $(python /root/openstack-neat/get-instances-ip.py)
do
    echo "ping $ip"
    ping -c 3 "$ip"
    sleep 1
done
