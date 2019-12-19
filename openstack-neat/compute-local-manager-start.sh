#!/bin/sh

for i in $(python /root/openstack-neat/get-hosts.py)
do

echo "start local manager in $i"

ssh root@$i "python /root/openstack-neat/start-local-manager.py &" &

done