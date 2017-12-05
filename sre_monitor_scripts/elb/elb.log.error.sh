#!/bin/bash

source ../lib

o_metric="elb.log.error"
o_error_pattern='^\[E '

check() {
    logfile="/opt/cloud/workspace/logs/elb_server/elb.log"
    date_format="%y%m%d %H:%M"
    report_log_error_num elb $logfile elb_server "$o_error_pattern" "$date_format" 
}


gendoc() {
    cat <<EOF
# $o_metric

## 概述

监控elb的错误日志数

## 原理

直接从日志文件中匹配,匹配模式为$o_error_pattern

## 处理方法

检查是否因发布造成的临时错误 todo
EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
