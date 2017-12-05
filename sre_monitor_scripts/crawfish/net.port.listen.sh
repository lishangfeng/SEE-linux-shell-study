#!/bin/bash

check() {
    true
}
gendoc() {
    cat <<EOF
# $METRIC

## 概述

该监控项检查crawfish是否监听在84411端口，以此来判断进程是否存活


## 原理

falcon自带功能

## 处理方法
看看进程是否还在，日志是否有报错，是否正在发布

EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
