#!/bin/bash

source ./lib

METRIC="ovs.kernel.flows.count"
STEP=60
TAGS=""

check() {
    FLOW_COUNT="$(ovs_dp_dumpflows_all | wc -l)"
    report_falcon $METRIC $FLOW_COUNT $STEP $TAGS
}

gendoc() {
    cat <<EOF
# $METRIC

## 概述

该脚本统计每一个网桥上的的内核流表项数量并求和，然后上报 Falcon

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
