#!/bin/bash

source ../lib

o_metric="controller.log.sqlite_lock"
o_error_pattern='sqlite.*locked'

check(){
    logfile="/opt/cloud/workspace/logs/host_server/host.log"
    date_format="%y%m%d %H:%M"
    report_log_error_num controller $logfile host_server "$o_error_pattern" "$date_format" "" "$o_metric"
}

gendoc() {
    cat <<EOF
# $o_metric

## 概述

Controller读取netmap数据库锁定错误监控

## 原理

直接从日志文件中匹配,匹配模式为$o_error_pattern

## 处理方法

重启netmap服务
EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
