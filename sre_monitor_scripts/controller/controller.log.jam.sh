#!/bin/bash

source ../lib

o_metric="controller.log.jam"
o_error_pattern="fp_worker_manager.*jam"

check(){
    logfile="/opt/cloud/workspace/logs/host_server/host.log"
    date_format="%y%m%d %H:%M"
    report_log_error_num controller $logfile host_server "$o_error_pattern" "$date_format" "" "$o_metric"
}

gendoc() {
    cat <<EOF
# $o_metric

## 概述

Controller过载监控

## 原理

直接从日志文件中匹配,匹配模式为$o_error_pattern

## 处理方法

观察流量特征，下发对应流表缓解压力
EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
