#!/bin/sh

for i in $(python /root/openstack-neat/get-instances-ip.py)
do

echo "copy cpu generator to ubuntu@$i..." >> distribute-sh.log
scp -i /root/testKey.pem -r /root/cpu-load-generator/ ubuntu@$i:~

echo "installing cpu-generator in ubuntu@$i..." >> distribute-sh.log
ssh -i /root/testKey.pem ubuntu@$i << eeooff

sudo apt-get install gcc make
y

eeooff

echo "finished in ubuntu@$i" >> distribute-sh.log
sleep 5

done 