#!/bin/bash

source ../lib
o_metric='mgw.log.unhealthy'
o_error_pattern='unhealthy'

check() {
    logfile="/var/log/cluster_daemon.log"
    date_format="%Y-%m-%d %H:%M"
    report_log_error_num mgw $logfile "mgw/bin/load_balancer" "$o_error_pattern" "$date_format" "" "$o_metric"
}


gendoc() {
    cat <<EOF
# $o_metric

## 概述

mgw unhealty监控

## 原理

直接从日志文件中匹配,匹配模式为$o_error_pattern

## 处理方法

TODO
EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
