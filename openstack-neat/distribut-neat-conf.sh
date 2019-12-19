#!/bin/sh

cp -b /root/openstack-neat/neat.conf /etc/neat/neat.conf

for i in compute1 compute2 compute3 compute4
do

scp /root/openstack-neat/neat.conf $i:/etc/neat/neat.conf
#ssh $i "timedatectl set-ntp no"

done