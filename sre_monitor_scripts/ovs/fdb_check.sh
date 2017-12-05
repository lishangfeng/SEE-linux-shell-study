#! /bin/bash

source ./lib

BRIDGE="breip"
GW_MAC_ADDR="00:00:5e:00:01:01"

function eip_ports_exists() {
    ovs_list_ports $BRIDGE | grep 'e-[a-z0-9]' > /dev/null
}

function gw_mac_exists() {
    ovs_fdb_show $BRIDGE | grep $GW_MAC_ADDR > /dev/null
}


METRIC="ovs_eipgw_fdb_mac_check"
RESULT_SUCC=1
RESULT_FAIL=0
STEP=60
TAGS=""

check() {
    # First, check the existence of e-port
    if eip_ports_exists; then
        # Second, check the gateway's mac
        if gw_mac_exists; then
            report_falcon $METRIC $RESULT_SUCC $STEP $TAGS
        else
            report_falcon $METRIC $RESULT_FAIL $STEP $TAGS
        fi
    else
        report_falcon $METRIC $RESULT_SUCC $STEP $TAGS
    fi
}

gendoc() {
    cat <<EOF
# $METRIC

##  概述

该脚本检查网桥 $BRIDGE 的 FDB 表中网关的 MAC 地址 $GW_MAC_ADDR 是否存在并上报至
Falcon，当网桥中存在 ports 并且网关的 MAC 地址不存在时上报0，否则上报1。

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
