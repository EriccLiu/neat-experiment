#!/bin/sh

for i in $(python /root/openstack-neat/get-instances-ip.py)
do

ssh -i /root/testKey.pem ubuntu@$i << eeooff

cd /home/ubuntu/cpu-load-generator/
./install-lookbusy.sh

eeooff

done