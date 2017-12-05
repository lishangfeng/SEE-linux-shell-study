# -*- coding: utf-8 -*-

import os
import socket
import datetime

zombie = []

if os.path.exists("/data/webapps/location"):
    line = os.popen("""/bin/sh /opt/meituan/apps/jumper-service/init.d/jumper-service status|grep 'process list'""").read()
    split_pid = line.split(':')[1][:-5].strip()
    pid_list = split_pid.split(',')

    listen_process_pid = int(os.popen("cat /var/sankuai/jumper-service.pid").read()[:-1])
    thread_count = int(os.popen('ps xH {0}|grep "\<{0}\>"|grep -v grep|grep -v ps|wc -l'.format(listen_process_pid)).read())
    print '\nmain_process: {0}, thread_count:{1}\n'.format(listen_process_pid, thread_count)
else:
    line = os.popen("""service jumper-service status|grep 'process list'""").read()
    split_pid = line.split(':')[1][:-5].strip()
    pid_list = split_pid.split(',')

    listen_process_pid = int(os.popen("cat /var/sankuai/jumper-service.pid").read()[:-1])
    thread_count = int(os.popen('ps xH {0}|grep "\<{0}\>"|grep -v grep|grep -v ps|wc -l'.format(listen_process_pid)).read())
    print '\nmain_process: {0}, thread_count:{1}\n'.format(listen_process_pid, thread_count)

with open("/data/applogs/jumper-service/logs/jumper.log") as fp:
    reversed_file = []
    for i in fp:
        reversed_file.insert(0, i.rstrip())
    for p in pid_list:
        user_info = None
        count = int(os.popen('ps xH {0}|grep "\<{0}\>"|grep -v grep|grep -v ps|wc -l'.format(p)).read())
        uptime = os.popen('ps -p {0} -o lstart='.format(p)).read().strip()
        uptime = datetime.datetime.strptime(uptime, "%a %b %d %H:%M:%S %Y")

        for line in reversed_file:
            if 'pid:{0}'.format(p) in line:
                user_info = line
                break
        if count < 4:
            if int(p) != listen_process_pid:
                if user_info:
                    alive_time = user_info.split()[0] + ' ' + user_info.split()[1].split(',')[0]
                    problem_pid = 'pid:{0}, thread_count:{1}, uptime:{2}, alive_time:{3}, {4}'.format(p, count, uptime, alive_time,
                                                                                                        user_info.split()[5])
                else:
                    problem_pid = 'pid:{0}, thread_count:{1}, uptime:{2}'.format(p, count, uptime)
                zombie.append(problem_pid)
            continue
        if user_info:
            alive_time = user_info.split()[0] + ' ' + user_info.split()[1].split(',')[0]
            print 'pid:{0}, thread_count:{1}, uptime:{2}, alive_time:{3}, {4}'.format(p, count, uptime, alive_time,
                                                                                        user_info.split()[5])
        else:
            print 'pid:{0}, thread_count:{1}, uptime:{2}'.format(p, count, uptime)
    print u'\n存在问题的进程列表:'
    for pid in zombie:
        print pid
    print u'\n说明: 进程和用户隐射关系是根据pid倒叙搜索日志得到的第一条,行尾时间为最近一条日志打印时间'
    print u'当前主机:{0} 上存在{1}个非正常用户进程'.format(socket.gethostname(), len(zombie))
    print u'当前主机:{0} 上存在{1}个正常用户进程'.format(socket.gethostname(), len(pid_list) - 1 - len(zombie))
