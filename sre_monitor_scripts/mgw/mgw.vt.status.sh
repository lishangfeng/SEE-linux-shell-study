#!/bin/bash


NICS=(
    vt0
    vt1
    vt2
    VT0
    VT1
    VT2
)

declare -A NIC_STATE_CODE
NIC_STATE_CODE=(
    [down]=0
    [DOWN]=0
    [UP]=1
    [up]=1
    [UNKNOWN]=2
    [unknown]=2
)

report_falcon() {
    value=$1
    tags=$2
    metric="mgw.VT.status"
    endpoint=`hostname -a`
    ts=$(date +%s)
    step=60
    counterType="GAUGE"

    curl -s -X POST -d "[{\"metric\":\"$metric\", \"endpoint\":\"$endpoint\", \"timestamp\":$ts, \"step\":60, \"value\":$value, \"counterType\":\"$counterType\", \"tags\":\"$tags\"}]" "http://127.0.0.1:1988/v1/push"

}


report_nic_state() {
    local nic=$1
    local nic_state=$2

    local nic_state_code=${NIC_STATE_CODE["$nic_state"]}
    if [ -z $nic_state_code ]; then
        nic_state_code=0
    fi
    report_falcon $nic_state_code "nic=$nic"
}


for nic in ${NICS[@]}; do
    ip link show $nic > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        nic_state=`ip link show $nic | awk -F 'state' '{printf $2}' | awk '{printf $1}'`
        report_nic_state $nic $nic_state
    fi
done
