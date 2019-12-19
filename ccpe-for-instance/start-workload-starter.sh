#!/bin/sh

rm -f /home/ubuntu/ccpe-for-instance/workload-starter.log
rm -f /home/ubuntu/ccpe-for-instance/workload-starter-console.log
echo "python2 workload-starter.py http://192.168.1.180:8081 108000 &..." >> distribute-sh.log
python2 /home/ubuntu/ccpe-for-instance/workload-starter.py http://192.168.1.180:8081 108000 >> /home/ubuntu/ccpe-for-instance/workload-starter-console.log &
