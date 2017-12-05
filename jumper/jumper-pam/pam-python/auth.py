# -*- coding=utf-8 -*-
import os
import json
import syslog
import socket
import urllib
import urllib2
from ConfigParser import ConfigParser


def pam_sm_authenticate(pam, flags, argv):
    host_info = get_host()
    try:
        config = ConfigParser()
        config.read('/etc/nss-http.conf')
        url = config.get('auth', 'auth_server') + '/api/pam/password?user_name={0}&host_ip={1}&host_name={2}'.format(
            pam.user, host_info['host_ip'], host_info['host_name']
        )
    except Exception as e:
        auth_log('auth', 'read config file error:[/etc/nss-http.conf]: {0}'.format(str(e)))
        pam.conversation(pam.Message(pam.PAM_ERROR_MSG, 'read config file error: /etc/nss-http.conf'))
        return pam.PAM_AUTH_ERR

    password = pam.conversation(pam.Message(pam.PAM_PROMPT_ECHO_OFF, "Password: ")).resp
    data = http_client(url, method='post', data=dict(password=password), timeout=config.get('auth', 'auth_timeout'))
    if not data:
        auth_log('auth', 'Request Auth API Error: {0}'.format(pam.user))
        pam.conversation(pam.Message(pam.PAM_ERROR_MSG, '\033[0;31mRequest Auth API Error, Please contact SRE.\033[0m'))
        return pam.PAM_AUTH_ERR
    else:
        data = json.loads(data)

    if data.get('code') == 200:
        os.popen('/sbin/getsudo daemon')
        open('/tmp/{0}_{1}'.format(pam.user, os.getpid()), 'a').close()
        auth_log('auth', 'auth success for {0}'.format(pam.user))
        return pam.PAM_SUCCESS
    elif data.get('code') == 3:
        auth_log('auth', '{0} session has expired'.format(pam.user))
    elif data.get('code') == 2:
        auth_log('auth', '{0} incorrect password'.format(pam.user))
    else:
        auth_log('auth', 'unknown error: {1} login failed, {1}'.format(pam.user, data))
    return pam.PAM_AUTH_ERR


def pam_sm_setcred(pam, flags, argv):
    return pam.PAM_SUCCESS


def pam_sm_acct_mgmt(pam, flags, argv):
    host_info = get_host()
    try:
        # 如果用户为登陆状态检查account字段, 1表示登陆状态|0表示非登陆状态
        login = 1
        if not os.path.isfile('/tmp/{0}_{1}'.format(pam.user, os.getpid())):
            login = 0
        config = ConfigParser()
        config.read('/etc/nss-http.conf')
        url = config.get('auth',
                         'auth_server') + '/api/pam/account?user_name={0}&host_ip={1}&host_name={2}&login={3}'.format(
            pam.user, host_info['host_ip'], host_info['host_name'], login
        )
    except Exception as e:
        auth_log('account', 'read config file error:[/etc/nss-http.conf]: {0}'.format(str(e)))
        return pam.PAM_AUTH_ERR

    data = http_client(url, timeout=config.get('auth', 'auth_timeout'))
    if not data:
        auth_log('account', 'Request Account API Error: {0}'.format(pam.user))
        return pam.PAM_AUTH_ERR
    else:
        data = json.loads(data)

    if data.get('code') == 200:
        auth_log('account', 'account success for {0}'.format(pam.user))
        return pam.PAM_SUCCESS
    elif data.get('code') == 1:
        auth_log('account', "{0} don't have permission".format(pam.user))
    else:
        auth_log('account', "unknown error: {0}, {1}".format(pam.user, data))
    return pam.PAM_AUTH_ERR


def pam_sm_open_session(pam, flags, argv):
    return pam.PAM_SUCCESS


def pam_sm_close_session(pam, flags, argv):
    auth_log('session', 'close session for {0}'.format(pam.user))
    try:
        os.remove('/tmp/{0}_{1}'.format(pam.user, os.getpid()))
    except OSError:
        pass
    return pam.PAM_SUCCESS


def pam_sm_chauthtok(pam, flags, argv):
    return pam.PAM_SUCCESS


def http_client(url, method='get', **kwargs):
    headers = kwargs.get('headers', dict())
    headers.update({'User-Agent': 'NSS-AUTH'})
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
        return urllib2.urlopen(request, timeout=int(kwargs.get('timeout', 10))).read().strip()
    except Exception as e:
        auth_log('http_exception', u'{0}'.format(str(e)))
        return False


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
        auth_log('auth', u'获取ip地址失败, 请排查.')
        ip = '127.0.0.1'
    return ip


def get_host():
    data = dict()
    data['host_name'] = socket.gethostname()
    data['user_id'] = os.getuid()
    data['host_ip'] = host_ip()
    return data


def auth_log(flag, msg):
    syslog.syslog('pam_python({0}): {1}'.format(flag, msg))
