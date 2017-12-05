#!/bin/bash

o_metric="dns-status"
check() {
    true
}

gendoc() {
    cat <<EOF
# $o_metric

## 概述

监控regiondns的状态


## 原理

发送dns请求，如应答错误或无法应答则上报错误，每分钟一次
由/opt/cloud/dns/scripts/falcon.py上报

## 处理方法
尝试重启对egion DNS服务，如果仍然没有恢复则联系研发排查

EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
