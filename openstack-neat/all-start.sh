#!/bin/sh

./compute-data-collector-start.sh
python start-global-manager.py &
python /neat/global/myClean.py &

sleep 2

./compute-local-manager-start.sh
