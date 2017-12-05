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

访问以下两个接口以确认netmap_proxy和netmap_writer存活

    http.url.check/url=/ping,port=8890,body=pong/Netmap-proxy service Bad!
    http.url.check/url=/ping,port=8892,body=pong/Netmap-writer service Bad!
    http.url.check/url=/ping,port=8875,body=pong [Netmap service Bad!]

## 处理方法

查看服务进程是否正常，服务整体Load是否高，定位是程序异常还是请求异常

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
