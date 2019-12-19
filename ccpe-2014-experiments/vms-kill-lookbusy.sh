#!/bin/sh

for ip in $(python /root/openstack-neat/get-instances-ip.py)
do
    echo "killing cpu-load-generator and lookbusy in ubuntu@$ip"
    echo "ssh -i /root/testKey.pem ubuntu@$ip -> ps -aux|egrep 'cpu-load-generator|lookbusy'|cut -c 9-15|xargs sudo kill -9"
    ssh -i /root/testKey.pem ubuntu@$ip "ps -aux|egrep 'workload-starter|cpu-load-generator|lookbusy'|cut -c 9-15|xargs sudo kill -9"
done
