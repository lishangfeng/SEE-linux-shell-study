# -*- coding: utf-8 -*-

import os
import time
import json
import socket

"""
以go重构版本调试脚本
"""

passwd_name = '{"type": "password", "name": "name", "value": "alex.wan", "pid": 111, "process_name":"crond"}'
passwd_uid = '{"type": "password", "name": "uid", "value": "1423194119", "pid": 111, "process_name":"crond"}'
group_gid = '{"type": "group", "name": "gid", "value": "1000014", "pid": 111, "process_name":"crond"}'
group_name = '{"type": "group", "name": "name", "value": "stree.meituan.sre", "pid": 111, "process_name":"crond"}'
group_all = '{"type": "group", "name": "", "value": "", "pid": 111, "process_name":"crond"}'


def fetch(data):
    socket = s
    socket.send(data)
    _data = socket.recv(10240)
    _j = json.loads(_data[16:])
    print json.dumps(_j, indent=4)
    print "*" * 20


if __name__ == '__main__':
    mypid = os.getpid()

    address = ('10.72.254.114', 8888)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(address)

    # passwd name
    print "passwd_name"
    fetch(passwd_name)
    time.sleep(5)
    print "passwd_uid"
    fetch(passwd_uid)

    print "group_gid"
    fetch(group_gid)

    print "group_name"
    fetch(group_name)

    print "group_all"
    fetch(group_all)

    s.close()
