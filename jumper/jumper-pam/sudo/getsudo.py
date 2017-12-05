#!/bin/env python
# -*- coding=utf-8 -*-

import os
import sys
import json
import stat
import syslog
import socket
import urllib
import urllib2
from ConfigParser import ConfigParser

reload(sys)
sys.setdefaultencoding('utf-8')


def get_colour(msg, colour='red'):
    try:
        if colour == 'red':
            return u'\033[31m{0}\033[0m'.format(msg)
        elif colour == 'green':
            return u'\033[32m{0}\033[0m'.format(msg)
        elif colour == 'yellow':
            return u'\033[33m{0}\033[0m'.format(msg)
        elif colour == 'blue':
            return u'\033[34m{0}\033[0m'.format(msg)
        else:
            return msg
    except UnicodeDecodeError:
        return msg


def auth_log(msg):
    syslog.syslog('GET_SUDO: {0}'.format(msg))


def host_ip():
    # dns放首位的原因是某些机器存在虚拟网卡接口(docker0, en0), 导致登陆拿到错误的ip
    # 通过dns查询,取得到的第一条ip记录
    ip = os.popen("""host %s |grep "has address"|head -n1|awk '{print $NF}'""" % socket.gethostname()).read().strip()
    if not len(ip):
        # CentOS6 获取本地第一个ip
        ip = os.popen("""/sbin/ifconfig | grep "Mask" | head -n1| awk -F'[ :]+' '{print $4}'""").read().strip()
        if not len(ip):
            # CentOS7 获取第一个ip
            ip = os.popen("""/sbin/ifconfig | grep "netmask"|head -n1|awk  '{print $2}'""").read().strip()
    if not len(ip):
        auth_log(u'get_sudo: 获取ip地址失败, 请排查.')
        ip = '127.0.0.1'
    return ip


def get_host():
    data = dict()
    data['host_name'] = socket.gethostname()
    data['user_id'] = os.getuid()
    data['host_ip'] = host_ip()
    return data


def sync_sudo(switch=None):
    host_info = get_host()
    try:
        config = ConfigParser()
        config.read('/etc/nss-http.conf')
        sudo_timeout = config.get('sudo', "sudo_timeout")
        sudo_file = '/etc/sudoers.d/' + config.get('sudo', 'sudoer_file')
        if switch == 'config':
            cache_api = config.get('sudo', 'sudo_server') + '/api/sudo/config?user_id={0}&host_ip={1}&host_name={2}'
            sudo_file = '/tmp/remote_sudo'
        else:
            cache_api = config.get('sudo', 'sudo_server') + '/api/sudo/cache?user_id={0}&host_ip={1}&host_name={2}'

        sudo_url = cache_api.format(host_info['user_id'], host_info['host_ip'], host_info['host_name'])

    except Exception as e:
        auth_log(u'解析配置文件失败:[/etc/nss-http.conf]: {0}'.format(str(e)))
        sys.exit()
    result = None
    try:
        result = http_client(sudo_url, timeout=sudo_timeout)
        data = json.loads(result)
    except:
        if switch is None or switch == 'config':
            print get_colour(u'sudo接口返回错误数据, 请排查--> {0}'.format(sudo_url))
        auth_log(u'sudo接口返回错误数据, 请排查--> {0}'.format(sudo_url))
        sys.exit()

    if data['code'] == 200:
        result = data['result']
        if isinstance(result, str) or isinstance(result, unicode):
            with open(sudo_file, 'w') as fd:
                fd.write(result)
                os.chmod(sudo_file, stat.S_IRUSR | stat.S_IRGRP)
        elif isinstance(result, list) and len(result) == 0:
            try:
                os.remove(sudo_file)
            except:
                pass
        else:
            if switch is None or switch == 'config':
                print get_colour(u'sudo接口返回数据类型不对, 请排查--> {0}'.format(sudo_url))
            auth_log(u'sudo接口返回数据类型不对, 请排查--> {0}'.format(sudo_url))
            sys.exit()
    else:
        if switch is None or switch == 'config':
            print get_colour(u'sudo接口请求非法, 请排查--> {0}'.format(sudo_url))
        auth_log(u'sudo接口请求非法, 请排查--> {0}'.format(sudo_url))
        sys.exit()

    if switch != 'daemon':
        if switch is None:
            os.system('cat {0}'.format(sudo_file))
        elif switch == 'config':
            print get_colour('**********' + u' sudo from mysql record ' + '**********')
            os.system('cat {0}'.format(sudo_file))
            print get_colour('\r\n**********' + u' sudo from redis cache  ' + '**********')
            old_sudo_file = '/etc/sudoers.d/' + config.get('sudo', 'sudoer_file')
            os.system('cat {0}'.format(old_sudo_file))
            print


def http_client(url, method='get', **kwargs):
    headers = kwargs.get('headers', dict())
    headers.update({'User-Agent': 'getsudo'})
    if method == 'post':
        if kwargs.get('data'):
            headers.update({'Content-Type': 'content-type: application/json'})
            data = json.dumps(kwargs.get('data'))
        else:
            data = urllib.urlencode(kwargs.get('values', dict()))
        request = urllib2.Request(url, headers=headers, data=data)
    else:
        request = urllib2.Request(url, headers=headers)
    try:
        return urllib2.urlopen(request, timeout=int(kwargs.get('timeout', 3))).read().strip()
    except Exception as e:
        auth_log(u'sudo接口错误: {0}'.format(str(e)))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] not in ['daemon', 'config']:
            print u'Usage:\r\n' \
                  u'getsudo         更新缓存并展示\r\n' \
                  u'getsudo daemon  更新缓存不展示\r\n' \
                  u'getsudo config  从db获取配置并且和cache中的对比\r\n'
            sys.exit()
        if sys.argv[1] == 'daemon':
            pid = os.fork()
            if pid == 0:
                sync_sudo(sys.argv[1])
            else:
                pass
        else:
            sync_sudo(sys.argv[1])
    else:
        sync_sudo()
