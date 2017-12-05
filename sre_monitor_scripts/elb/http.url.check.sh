#!/bin/bash

o_metric=http.url.check

check() {
    true
}

gendoc() {
    cat <<EOF
# $o_metric

## 概述

这个监控项在falcon实现，不需要脚本收集

## 原理

访问以下两个接口以确认elb server存活

    http.url.check/url=/ping,port=8881,body=pong [ELB service Bad!]

## 处理方法

查看服务进程是否正常，服务整体Load是否高，定位是程序异常还是请求异常

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
