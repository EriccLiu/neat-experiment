#/bin/bash

#rm -rf /root/openstack-neat
#rm -rf /root/ccpe-2014-experiments

chmod -R 755 /root/openstack-neat
chmod -R 755 /root/ccpe-2014-experiments

for i in 1 2 3 4
do

ssh compute$i rm -rf /root/openstack-neat
scp -r /root/openstack-neat compute$i:/root
ssh compute$i chmod -R 755 /root/openstack-neat
ssh compute$i rm -rf /usr/local/lib/python2.7/dist-packages/openstack_neat-0.1-py2.7.egg/neat/
ssh compute$i cp -rb /root/openstack-neat/neat/ /usr/local/lib/python2.7/dist-packages/openstack_neat-0.1-py2.7.egg/

done