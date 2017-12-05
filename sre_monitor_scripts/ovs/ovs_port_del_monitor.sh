#! /bin/bash

source ./lib

METRIC="ovs.port.delete.monitor"
RESULT_SUCC=0
RESULT_FAIL=1
STEP=60
TAGS=""

check() {
    SERVER_LIST=$(ps aux | grep qemu | grep -o '/opt/cloud/workspace/servers/[-a-z0-9]\+' | uniq)
    DP_PORTS="$(ovs_dp_ports)"

    RESULT=$RESULT_SUCC
    for SERVER_PATH in $SERVER_LIST; do
        for IFNAME in $(grep -o 'ifname[''": ]\+[^''"]\+' "$SERVER_PATH/desc" | sed 's/.*[''"]//'); do
            echo $DP_PORTS | grep -q "\<$IFNAME\>\s[0-9]\+/[0-9a-z]\+:"
            if [ "$?" == "1" ]; then
                RESULT=$RESULT_FAIL
                break
            fi
        done
        if [ "$RESULT" == "$RESULT_FAIL" ]; then
            break
        fi
    done
    report_falcon $METRIC $RESULT $STEP $TAGS
}

gendoc() {
    cat <<EOF
# $METRIC

## 概述

该脚本检查当前运行的虚拟机的虚拟网卡在 OVS 的内核端口是否存在，如果不存在则报警

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
