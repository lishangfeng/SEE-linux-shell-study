#! /bin/bash

source ./lib

BRIDGE="brpri"
METRIC="ovs.dumpflows."$BRIDGE".number"
STEP=60
TAGS=""

report() {
    # Flow entries should contains 'priority'
    FLOW_COUNT="$(ovs_of_dumpflows_with_br $BRIDGE | grep 'priority' | wc -l)"
    report_falcon $METRIC $FLOW_COUNT $STEP $TAGS
}

gendoc() {
    cat <<EOF
# $METRIC

## 概述

该脚本统计网桥 $BRIDGE 中的 OpenFlow 流表项数量并上报至 Falcon

EOF
}

[ "$#" -gt 0 ] || set -- report
"$@"
