#!/bin/sh

for i in $(python /root/openstack-neat/get-hosts.py)
do

echo "start data collector in $i"

ssh root@$i "python /root/openstack-neat/start-data-collector.py &" &

done