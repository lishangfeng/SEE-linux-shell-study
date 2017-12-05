#!/usr/bin/env bash

set -e
set -x

WORK_DIR='/opt/meituan/apps/jumper-service'

sed -i 's@/data/webapps/${service_name}/current/@/opt/meituan/apps/jumper-service@g' init.d/jumper-service

[ -d '/data/applogs/jumper-service/logs' ] || mkdir -p /data/applogs/jumper-service/logs

if [ -f /opt/rh/python27/enable ]; then
    source /opt/rh/python27/enable
else
    echo "Not found: /opt/rh/python27/enable"
    return 1
fi

[ ! -f /usr/bin/virtualenv ] && pip install virtualenv
[ ! -f .venv/bin/activate ] && virtualenv -p "/opt/rh/python27/root/usr/bin/python"  .venv

source .venv/bin/activate

pip install --upgrade pip wheel setuptools --index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r ./requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 注册服务 plus agnet 没权限注册
#cp ./init.d/jumper-service /etc/init.d/
#chmod o-x /etc/init.d/jumper-service

# reload service
sh ./init.d/jumper-service restart &>/dev/null
sleep 2
exit 0
