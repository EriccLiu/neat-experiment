#!/bin/sh

rm -f workload-distributor-server.log

for i in $(python /root/openstack-neat/get-instances-ip.py)
do

echo "start workload starter in ubuntu@$i..."
ssh -i /root/testKey.pem ubuntu@$i "/home/ubuntu/ccpe-for-instance/start-workload-starter.sh"
done

python2 workload-distributor.py planetlab-selected &>> workload-distributor-server.log
