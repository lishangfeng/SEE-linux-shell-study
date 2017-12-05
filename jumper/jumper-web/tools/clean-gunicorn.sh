#!/bin/bash

day=$(date "+%Y%m%d")
mv /data/applogs/jumper-web/logs/gunicorn-access.log{,-${day}}
mv /data/applogs/jumper-web/logs/gunicorn-error.log{,-${day}}
kill -USR1 $(cat /opt/meituan/apps/jumper-web/gunicorn.pid)
find /data/applogs/jumper-web/logs/ -type f -name gunicorn* -mtime +7 -exec rm -f {} \;
