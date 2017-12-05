#!/bin/bash

o_metric="dns-resolve-timeout"
check() {
    true
}

gendoc() {
    cat <<EOF
# $o_metric

## 概述

dns响应时间监控


## 原理

检查日志中解析时间，出现3次超过20ms作为错误，每分钟一次,由regiondns和hostdns上报
日志文件在/opt/cloud/workspace/logs/dns_server下


## 处理方法
排查解析慢原因

EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
