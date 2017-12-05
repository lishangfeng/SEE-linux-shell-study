#! /bin/bash

source ./lib

METRIC="ovs.vswitchd.cpu"
STEP=60
TAGS=""

check() {
    if is_ovs_dpdk_running; then
        TOTAL_CPU=0
        for CPU in $(ovs_appctl dpif-netdev/pmd-stats-show | grep "processing cycles:" | grep -o "[0-9.]\+%" | grep -o "[0-9.]\+"); do
            TOTAL_CPU=$(python -c "print($TOTAL_CPU + $CPU)")
        done
    else
        TOTAL_CPU=$(top -b -n 1 -d 5.5 -p $(ps -A|awk '/ovs-vswitchd/{print $1}')| grep ovs-vswitchd | awk '{print $9}')
    fi
    report_falcon $METRIC $TOTAL_CPU $STEP $TAGS
}

gendoc() {
    cat <<EOF
# $METRIC

## 概述

该脚本计算 OVS 的 CPU 使用率并上报至 Falcon

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
