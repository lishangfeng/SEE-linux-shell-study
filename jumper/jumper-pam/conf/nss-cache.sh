#!/usr/bin/env bash
# chkconfig: - 30 74
# description:  This is a daemon which handles app

if [ -f /etc/init.d/functions ]; then
    . /etc/init.d/functions
elif [ -f /etc/rc.d/init.d/functions ] ; then
    . /etc/rc.d/init.d/functions
else
    exit 0
fi

# Source networking configuration.
. /etc/sysconfig/network
# Check that networking is up.

[ ${NETWORKING} = "no" ] && exit 0

# service name
service_name="nss-cache"

# pid文件位置
pidfile="/var/run/nss-cache.pid"

# log dir
logdir="/var/log/nss-cache.log"

# 执行的命令
command="/usr/sbin/nss-cache"

[ -f $config ] || exit 1

RETVAL=0

# 终端颜色
Red='\033[0;31m'
Color_Off='\033[0m'
Green='\033[0;32m'


status() {
    # 分3种情况，
    # 1, pid文件存在，同时文件中的pid进程存在， 返回程序running
    # 2, pid文件存在，同时文件中pid进程不存在， 返回程序未启动，让start方法保证进程running
    # 3, pid文件不存在，返回进程未启动，让start保证僵尸进程kill掉，同时启动新进程

    if [ -f "$pidfile" ];then
        pid=`cat "$pidfile" 2>/dev/null`
        if ps -p $pid > /dev/null
        then
            start_time=`ps -p ${pid} -o lstart|grep -v 'STARTED'`
            t_count=`ps xH|grep ${pid}|grep -v grep|wc -l`
            p_count=`ps aux|grep "${command}"|grep -v "grep"|awk '{print $2}'|wc -l`
            memory_used=`cat /proc/$pid/status | grep RSS|awk '{print $2}'`" kB"
            printf "${Green}         status: running${Color_Off}\n"
            printf "${Green}  process count: ${p_count}${Color_Off}\n"
            printf "${Green}threads/process: ${t_count}${Color_Off}\n"
            printf "${Green}   process list: ${pid}${Color_Off}\n"
            printf "${Green}    memory used: ${memory_used}${Color_Off}\n"
            printf "${Green}         uptime: ${start_time}${Color_Off}\n"
            RETVAL=0
        else
            printf "${Green}         status: stopped${Color_Off}\n"
            RETVAL=1
        fi
    else
        printf "${Green}         status: stopped${Color_Off}\n"
        RETVAL=1
    fi
}

start() {
    # pid文件存在
    if [ -f "$pidfile" ];then
        pid=`cat "$pidfile" 2>/dev/null`
        if ps -p $pid > /dev/null
        then
            printf "${Red}${service_name} is running with pid $pid ${Color_Off}\n"
            RETVAL=0
        else
            nohup $command >>$logdir 2>&1 &
            usleep 10000
            pid=`cat "$pidfile" 2>/dev/null`
            if ps -p $pid > /dev/null
            then
                RETVAL=$?
                action $"Starting $service_name: " /bin/true
            else
                RETVAL=1
                action $"Starting $service_name: " /bin/false
            fi
        fi
    else
        pids=`ps aux|grep "${command}"|grep -v "grep"|awk '{print $2}'`
        for p in $pids
        do
            # 排除docker宿主机
            ppid=`ps -o ppid= -p $p`
            if [ $ppid -eq 1 ]
            then
                kill -9 $p
            fi
        done
        nohup $command >>$logdir 2>&1 &
        sleep 0.5
        pid=`cat "$pidfile" 2>/dev/null`
        if ps -p $pid > /dev/null
        then
            RETVAL=$?
            action $"Starting $service_name: " /bin/true
        else
            RETVAL=1
            action $"Starting $service_name: " /bin/false
        fi
    fi
}

stop() {
    pids=`ps aux|grep "${command}"|grep -v "grep"|awk '{print $2}'`
    for p in $pids
    do
        # 排除docker宿主机
        ppid=`ps -o ppid= -p $p`
        if [ $ppid -eq 1 ]
        then
            kill -9 $p
        fi
    done
    rm -f /var/run/nss-cache.pid
    rm -f /var/run/nss-cache.sock
    RETVAL=0
    action $"Stopping $service_name: " /bin/true
}

restart() {
    stop
    start
}

case "$1" in
    start)
    start
    ;;
    stop)
    stop
    ;;
    restart)
    restart
    ;;
    r)
    restart
    ;;
    status)
    status
    ;;
    s)
    status
    ;;
    *)
    printf "${Red}Usage: service ${service_name} {start|stop|restart|status}${Color_Off}\n"
    RETVAL=1
esac

exit $RETVAL
