#!/usr/bin/env bash

set -e
set -x

WORK_DIR='/opt/meituan/apps/jumper-web'

[ -d '/data/applogs/jumper-web/logs' ] || mkdir -p /data/applogs/jumper-web/logs

[ -f 'instance/config.py' ] || mkdir -p instance && touch instance/config.py

[ -f "/data/webapps/location" ] || mkdir -p /data/webapps/ && echo "location=mt" > /data/webapps/location

if [ -f /opt/rh/python27/enable ]; then
    source /opt/rh/python27/enable
else
    echo "Not found: /opt/rh/python27/enable"
    exit 1
fi

[ ! -f /usr/bin/virtualenv ] && pip install virtualenv
[ ! -f venv/bin/activate ] && virtualenv -p "/opt/rh/python27/root/usr/bin/python"  venv

source venv/bin/activate

pip install --upgrade pip wheel setuptools --index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r ./requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# clean gunicorn log
crontab -l | grep 'clean-gunicorn.sh' -q || ( crontab -l ; echo "59 23 * * * sh ${WORK_DIR}/tools/clean-gunicorn.sh &>/dev/null" ) | crontab -

# clean /dev/shm cache file
crontab -l | grep 'clean_cache.py' -q || ( crontab -l ; echo "0 23 * * * python ${WORK_DIR}/tools/clean_cache.py &>/dev/null" ) | crontab -

# reload gunicorn
sh init.d/mt-jumper-web stop &>/dev/null
sleep 2
sh init.d/mt-jumper-web start &>/dev/null
sleep 2

