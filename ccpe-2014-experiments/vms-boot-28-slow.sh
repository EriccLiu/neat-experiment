#!/bin/sh

for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28
do
    echo "creating ubuntu$i"
    openstack server create --flavor pico --image neat-ubuntu \
    --security-group mySecGroup --nic net-id=3885d567-79b7-480b-9dd1-9d6d32f225d0 \
    --key-name testKey "ubuntu$i"
    sleep 5
done
