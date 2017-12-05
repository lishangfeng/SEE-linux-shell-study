#! /bin/bash

source ./lib

METRIC='ovs.port.exist.verify'
RESULT_SUCC=0
RESULT_FAIL=1
ERROR=''
STEP=60
TAGS=""

VM_PATH="/opt/cloud/workspace/servers"
CONTAINER_PATH="/opt/cloud/workspace/containers"

get_br_ifname_pairs_by_desc() {
    local DESC="$1"
    echo $DESC | python -c "import sys, json
for nic in json.loads(sys.stdin.read())['nics'] or []:
    print nic['bridge'], nic['ifname']"
}

get_running_target_br_ifname_pairs() {
    local target_path=$1
    local target
    local target_pid
    local desc
    local name
    local container_id
    local container_status

    [ -d "$target_path" ] || return
    for target in $(ls $target_path 2> /dev/null); do
        [ -e $target_path/$target/desc ] || continue
        desc="$(cat $target_path/$target/desc)"
        if [ "$target_path" == "$VM_PATH" ]; then
            [ -e $target_path/$target/pid ] || continue
            target_pid="$(sudo head -n 1 $target_path/$target/pid | awk -F, '{print $1}' | grep -o '[0-9]\+')"
            [ -n "$target_pid" ]  && [ -d /proc/$target_pid ] || continue
            get_br_ifname_pairs_by_desc "$desc"
        elif [ "$target_path" == "$CONTAINER_PATH" ]; then
            [ -e $target_path/$target/containers ] || continue
            # Content of containers may be '["container_id_0", "container_id_1"]'
            # And the first one matters
            container_id="$(sudo cat $target_path/$target/containers | awk -F, '{print $1}' | grep -o '[0-9a-zA-Z]\+')"
            container_status="$(sudo docker inspect $container_id | grep Status | awk -F: '{print $2}' | grep -o '[a-zA-Z]\+')"
            if [ "$container_status" == "running" ]; then
                get_br_ifname_pairs_by_desc "$desc"
            fi
        fi
    done
}

check() {
    RESULT=$RESULT_SUCC
    local vm_br_if_pairs="$(get_running_target_br_ifname_pairs $VM_PATH)"
    local container_br_if_pairs="$(get_running_target_br_ifname_pairs $CONTAINER_PATH)"
    local dp_info="$(ovs_dp_ports)"
    local len=$(echo "$dp_info" | wc -l)
    local dp_bridges="$(echo "$dp_info" | grep 'br[_a-zA-Z0-9-]\+:' | awk -F: '{print $1}')"

    local brn
    local dp_ports
    local check_pair
    local target_br
    local br
    local p

    for br in $dp_bridges; do
        brn="$(echo "$dp_bridges" | grep -A1 $br | grep -v $br)"
        dp_ports=$(echo "$dp_info" | grep  -A $len "$br:" | grep -B $len "$brn:" | grep -o '\<[ne]-[a-z0-9]\+\>')
        for p in $dp_ports; do
            if echo "$vm_br_if_pairs" | grep -q "$p"; then
                check_pair="$vm_br_if_pairs"
            elif echo "$container_br_if_pairs" | grep -q "$p"; then
                check_pair="$container_br_if_pairs"
            else
                RESULT=$RESULT_FAIL
                __errmsg "EXISTS ERROR: $p should not exist in $br"
                __errmsg "  Fix it: sudo /usr/local/bin/ovs-vsctl del-port $br $p"
                continue
            fi
            target_br="$(echo "$check_pair" | grep "$p" | awk '{print $1}')"
            if [ "$br" != "$target_br" ]; then
                RESULT=$RESULT_FAIL
                __errmsg "MISMATCH ERROR: <port> $p should exist in $target_br rather than $br"
                __errmsg "  Fix it: sudo /usr/local/bin/ovs-vsctl del-port $br $p"
                __errmsg "  Fix it: sudo /usr/local/bin/ovs-vsctl add-port $target_br $p"
            fi
        done
    done
    report_falcon $METRIC $RESULT $STEP $TAGS
}

gendoc() {
    cat <<EOF
# $METRIC

## 概述

该脚本检查当前网桥中的存在的网卡是否符合预期。

## 原理

获取当前运行的 Qemu 或者 Docker 实例，通过检查 /opt/cloud/workspace/{servers|containers}/{ID}/desc 中的网卡信息判断 OVS/MVS 网桥中虚拟机网卡是否符合预期，如果不符合则上报错误信息。

不符合预期的情况有两种：
1. 虚拟机未运行，网卡不应该任何一个网桥中存在
2. 虚拟机已运行，网卡存在于错误的网桥中

单独运行脚本时，如果出现不符合预期的情况，会给出错误信息。

## 处理方法

运行脚本，通过脚本给出的命令进行修复

		./ovs_port_validate_monitor.sh.sh 2>&1 | grep 'Fix it' | cut -f2 -d:

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
