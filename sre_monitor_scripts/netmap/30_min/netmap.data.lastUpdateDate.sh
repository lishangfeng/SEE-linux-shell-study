#!/bin/bash

source ../../lib

o_metric="netmap.data.lastUpdateDate"
o_logfile="/opt/cloud/workspace/logs/netmap_server/netmap.log"


check() {
    local result=0
    local step=1800
    local tags="service=netmap"

    if [ -f "$o_logfile" ]; then
        local last_update_time=`grep -i "Recieve complete"  "$o_logfile" | tail -n 1 | awk '{print $2,$3}'`
        if [ -z "$last_update_time" ]; then
            __errmsg "没有匹配到Recivev complete字段，可能是日志格式更改造成"
            result=-1
        else
            local last_update_second=`date -d "$last_update_time" +%s`
            local current_second=`date +%s`
            result=$(( $(($current_second - $last_update_second)) / 86400))
        fi
    elif [ `ps aux | grep netmap_server | wc -l` -gt 1 ]; then
        __errmsg "进程netmap_server存在，但是对应的日志文件${o_logfile}不存在"
        retuslt=-1
    else
        result=0
    fi
    report_falcon "$o_metric" "$result" "$step" "$tags"
}


gendoc() {
    cat <<EOF
# $o_metric

## 概述

netmap服务数据过期监控

## 原理

匹配日志${o_logfile}中最后下载成功时间,如果最后下载成功时间距离当前时间超过一天则报警

## 处理方法

todo zhouyousong

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"

