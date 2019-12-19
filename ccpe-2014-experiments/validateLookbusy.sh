#!/bin/sh

for i in $(python /root/openstack-neat/get-instances-ip.py)
do

echo "validate ubuntu@$i..."
ssh -i /root/testKey.pem ubuntu@$i << eeooff 

lookbusy -h

eeooff

done
