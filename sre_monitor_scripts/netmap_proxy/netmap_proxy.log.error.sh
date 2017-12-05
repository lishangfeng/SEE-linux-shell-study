#!/bin/bash

source ../lib

o_metric="netmap_proxy.log.error"
o_error_pattern='^\[E '

check() {
    logfile="/opt/cloud/workspace/logs/netmap_proxy_server/netmap_proxy.log"
    date_format="%y%m%d %H:%M"
    report_log_error_num netmap_proxy $logfile netmap_proxy "$o_error_pattern" "$date_format"
}


gendoc() {
    cat <<EOF
# $o_metric

## 概述

监控netmap_proxy的错误日志数

## 原理

直接从日志文件中匹配, 匹配模式为 $o_error_pattern

## 处理方法

检查是否因发布造成的临时错误
EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
