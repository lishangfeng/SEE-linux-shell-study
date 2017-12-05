#!/bin/bash

check() {
    true
}
gendoc() {
    cat <<EOF
# $METRIC

## 概述

这个监控项在falcon实现，不需要脚本收集

## 原理

http.url.check访问/eipnetdescs/fake，每分钟一次

## 处理方法
查看服务进程是否正常，服务整体Load是否高，定位是程序异常还是请求异常

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
