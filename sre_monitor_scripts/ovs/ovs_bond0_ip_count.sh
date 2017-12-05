#! /bin/bash

source ./lib

METRIC="ovs.bond0.ip.count"
RESULT_SUCC=0
RESULT_FAIL=1
STEP=60
TAGS=""

check() {
    IP_COUNT=$(ip r | grep '^10\.[.0-9]\+\/[0-9]\+' | grep link | wc -l)
    if [ $IP_COUNT -eq 1 ] ; then
        report_falcon $METRIC $RESULT_SUCC $STEP $TAGS
    else
        report_falcon $METRIC $RESULT_FAIL $STEP $TAGS
    fi
}

gendoc() {
    cat <<EOF
# $METRIC

## 概述

该脚本检查宿主机宿主机上的路由表的中是否有且只有一条指向管理网网段的路由，如果不是则上报$RESULT_FAIL，否则上报 $RESULT_SUCC

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
