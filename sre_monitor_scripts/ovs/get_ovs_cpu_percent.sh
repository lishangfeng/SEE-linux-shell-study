#! /bin/bash

source ./lib

HOST_PORT=$(grep "\<port\>" /etc/mclouds/host.conf | grep -o "[0-9]\+")
HOST_STAT_URL="http://127.0.0.1:$HOST_PORT/stats"

METRIC="ovs.controller.cpu_percent"
STEP=60
TAGS=""

check() {
    CPU="$(curl -s "$HOST_STAT_URL" | \
           python -c "import sys, json; print(json.loads(sys.stdin.read())['ovs_controller']['cpu_percent'])")"
    report_falcon $METRIC $CPU $STEP $TAGS

}

gendoc() {
    cat <<EOF
# $METRIC

## 概述

该脚本通过 Host 服务的 $HOST_STAT_URL 接口获取 OpenFlow 控制器的 CPU 使用率并上报至 Falcon

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
