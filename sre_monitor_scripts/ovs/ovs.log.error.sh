#! /bin/bash

source ./lib

METRIC="ovs.vswitchd.ERRanddisconnecting"
o_metric="ovs.log.error"
STEP=60
TAGS=""

PATTERN=`date -u '+%Y-%m-%dT%H:%M'  -d'-1 minute'`
LOGFILE="/usr/local/var/log/openvswitch/ovs-vswitchd.log"

check() {
    ERR_NUM=`grep "$PATTERN" $LOGFILE | grep  "ERR"| grep "disconnecting" | wc -l`
    report_falcon $METRIC $ERR_NUM $STEP $TAGS
    report_falcon $o_metric $ERR_NUM $STEP $TAGS
}

gendoc() {
    cat <<EOF
# $METRIC

## 概述

该脚本检查距离当前时间一分钟以内 OVS 的日志文件（$LOGFILE) 中的同时包含 ERR 和 disconnecting 日志条目的数量并上报至 Falcon

EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
