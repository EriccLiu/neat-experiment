#!/bin/sh

for ip in $(python /root/openstack-neat/get-instances-ip.py)
do
    echo $(ssh -i /root/testKey.pem ubuntu@$ip "cd /home/ubuntu/ccpe-for-instance/")
done
