#!/bin/bash

source ../lib

o_metric="security.log.error"
o_error_pattern='(ERROR)|(WARN)'

security_check() {
    logfile="/opt/cloud/workspace/logs/security/security.log"
    date_format="%y%m%d %H:%M"
    report_log_error_num security $logfile security_services "$o_error_pattern" "$date_format" 
}

detector_check() {
    logfile="/opt/cloud/network-detector/flow_detector/log/flow_detector.log"
    date_format="%Y-%m-%d %H:%M"
    report_log_error_num security_detector $logfile flow_detector "$o_error_pattern" "$date_format" 
}

blackdrags_check() {
    logfile="/opt/cloud/network-blackholedragcluster-service/log/bd.log"
    date_format="%y%m%d %H:%M"
    report_log_error_num security_blackdrags $logfile blackdragservices "$o_error_pattern" "$date_format" 
}

check() {
    security_check
    detector_check
    blackdrags_check
}

gendoc() {
    cat <<EOF
# $o_metric

## 概述

监控security的错误日志数

## 原理

直接从日志文件中匹配,匹配模式为$o_error_pattern

## 处理方法

检查是否因发布造成的临时错误
EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
