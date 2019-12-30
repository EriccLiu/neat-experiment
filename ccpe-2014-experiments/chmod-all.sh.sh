#/bin/bash

chmod -R 755 /root/openstack-neat
chmod -R 755 /root/ccpe-2014-experiments

for i in 1 2 3 4
do

ssh compute$i chmod -R 755 /root/openstack-neat

done