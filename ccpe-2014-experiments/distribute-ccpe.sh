#!/bin/sh

for i in $(python /root/openstack-neat/get-instances-ip.py)
do

echo "copy ccpe for instance to ubuntu@$i..." >> distribute-sh.log
scp -i /root/testKey.pem -r /root/ccpe-for-instance/ ubuntu@$i:~

echo "prepare for workload starter in ubuntu@$i..." >> distribute-sh.log
ssh -i /root/testKey.pem ubuntu@$i << eeooff

cd /home/ubuntu/ccpe-for-instance/
sudo python get-pip.py
sudo pip install --ignore-installed requests

eeooff

echo "finished preparing pip in ubuntu@$i" >> distribute-sh.log
sleep 5

done