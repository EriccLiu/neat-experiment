#!/bin/sh

if [ $# -ne 1 ]
then
    echo "You must specify the name of the log collection file name"
    exit 1
fi


mkdir "/root/$1"
cd "/root/$1"

mkdir "controller"
cp -rb /var/log/neat/* controller
for i in 1 2 3 4
do
mkdir "compute$i"
scp compute$i:/var/log/neat/* compute$i
done

cd /root/ccpe-2014-experiments/results
./db-dump.sh
cp -b db.sql /root/$1
cp -b db.tar.gz /root/$1