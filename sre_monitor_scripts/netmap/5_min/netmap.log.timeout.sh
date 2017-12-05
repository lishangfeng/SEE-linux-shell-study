#!/bin/bash

source ../../lib

o_metric="netmap.log.timeout"
o_tags="service=netmap"
o_timeout_pattern='((HTTP 599)|(HTTP 504))'
o_logfile="/opt/cloud/workspace/logs/netmap_server/netmap.log"

check() {
    local date_format="%y%m%d %H:%M"
    local result=0

    pattern="${date_format}.*${o_timeout_pattern}"

    if [ `process_exist "netmap_server"` -eq 1 ]; then
       result=`get_pattern_log_num "$pattern" "$o_logfile"`
       report_falcon "$o_metric" "$result" 300 "$o_tags"
    fi
}


gendoc() {
    cat <<EOF
# $o_metric

## 概述

监控netmap的超时日志数

## 原理

直接从日志文件中匹配,匹配模式为$o_timeout_pattern

## 处理方法

检查下是否可以正常访问netmap_proxy服务器, todo
EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
