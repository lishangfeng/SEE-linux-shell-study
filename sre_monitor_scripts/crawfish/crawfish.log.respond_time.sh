#!/bin/bash

source ../lib

METRIC='network_region_respond_time'
STEP=60
TAGS="service=crawfish"

LOG_FILE="/opt/logs/crawfish/access.`date +"%Y-%m-%d"`.log"
CURRENT_TIME=$(date +"%d/%b/%Y:%H:%M" -d'1 minutes ago')

check(){
    local RESULT=0

    if [ -f $LOG_FILE ]; then
        RESULT=`grep "$CURRENT_TIME" "$LOG_FILE" | awk '{printf $8"\n"}' | sort -n  | tail -n1`
    elif [ `ps aux | grep crawfish| wc -l` -gt 1 ]; then
        # 如果进程存在，但是日志文件不在，可能是由于开发修改了日志目录，为了防止监控失效，我们给出一个报警
        RESULT=-1
        echo "crawfish进程存在但是日志文件不存在"
    else
        RESULT=0
    fi
    report_falcon $METRIC $RESULT $STEP $TAGS
    report_falcon 'crawfish.log.respond_time' $RESULT $STEP $TAGS

}

gendoc() {
    cat <<EOF
# $METRIC

## 概述

监控crawfish的响应时间
## 原理

通过日志文件获取响应时间，取一分钟内最大的那个响应时间,但是这个值只是一个参考值。
详细的性能分析参见 http://octo.sankuai.com/data/tabNav?appkey=com.sankuai.cloud.cloudpublic.network

会有以下几种情况出现：
1. crawfish进程存在但是日志文件不存在，返回9999，falcon报警。
2. crawfish进程不存在，返回0。
3. 进程存在，日志文件存在，返回一分钟内最大响应时间


## 处理方法

看下日志文件，会有以下几种可能
1.只有少数请求响应时间长，忽略该次报警
2.很多请求响应时间长，检查系统负载、io、网络等状态
EOF
}


[ "$#" -gt 0 ] || set -- check
"$@"
