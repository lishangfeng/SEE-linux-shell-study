# -*- coding:utf-8 -*-

import hmac
import json
import logging
import netifaces as nic
import os
import re
import shutil
import socket
import sys
import time
from base64 import b64encode
from datetime import datetime
from hashlib import sha1
from socket import gaierror

import paramiko
import requests
from app.lib.async import Async
from app.lib.http_client import http_client
from app.lib.notice import Notice
from paramiko.py3compat import decodebytes
from termcolor import colored

from app.ssh_server.init import config

reload(sys)
sys.setdefaultencoding("utf-8")


def navigation(user_info):
    nav = u"""
所有支持的命令:\r

    h/H/help                    :显示帮助信息\r
    i/info/information          :展示当前登录信息\r
    r/R                         :查看后端服务器的登录历史\r
    p/password                  :更新密码\r
    u/U/user                    :查看当前登录用户信息\r
    id                          :查看指定用户信息\r
    ssh                         :ssh命令\r
    ping                        :ping命令\r
    history                     :查看历史命令\r
    q/exit                      :登出系统\r\n
    技能(键入命令查看帮助)\r
    getapp                      :获取应用机器列表\r
    gethost                     :根据ip或hostname获取机器信息\r
    pssh                        :批量执行命令 (非交互式)\r
    plog                        :批量查询日志 (仅限在上海标准日志目录机器使用)\r
    play                        :屏幕录像回放\r
  {news}
\r"""
    news = ai(user_info)
    if news:
        news = '\n' + news + '\r\n'
    return colored(nav.format(news=news), color='green')


def ai(user_info):
    # 降级 -> 终端新闻 -> 生日提醒 -> ai提醒 ->
    if not config.get('dynamic_password'):
        return colored(config.get('degrade_news'), color='red')
    if config.get('terminal_news'):
        return colored(config.get('terminal_news'), color='red')
    if user_info.get('birthday') and birthday_check(user_info.get('birthday')):
        if ismidnight():
            return colored(config.get('midnight_birthday_news'), color='cyan')
        return colored(config.get('birthday_news'), color='cyan')
    return ai_check() or ''


def birthday_check(birthday):
    today = datetime.now().date()
    bir_day = datetime.strptime(birthday, "%Y-%m-%d %H:%M:%S").date()
    if bir_day.month == today.month and bir_day.day == today.day:
        return config['ai_news']['deep_night']


def ai_check():
    # 工作时间提醒，明天气温提醒，节日提醒（周末），爆炸新闻提醒等等
    if ismidnight():
        return colored(config['ai_news']['deep_night'], color='cyan')


def ismidnight():
    today = datetime.now()
    if 23 <= today.hour or today.hour <= 5:
        return True


def invalid_navigation(user_name, flag):
    """
    1: 系统中不存在的非法用户
    2: 未开通终端权限的用户
    3: 离职用户
    """
    collection = {
        1: u"是系统中不存在的非法用户, 请核对后登录!",
        2: u"未开通终端权限, 请前往 https://wiki.sankuai.com/pages/viewpage.action?pageId=624539419",
        3: u"显示您已经离职, 请误重试, 否则报警!",
        4: u"最近连续输入密码错误超过6次, 账号已锁定, 请前往 http://ops.sankuai.com/workflow/#/start/jumper-unlock",
        5: u"登录时遇到Jumper接口出错, 请联系alex.wan 或 tanxiaohang 排查, 或者重试一下!"
    }

    nav = u"""
您的账号%s %s
    \r
"""
    return get_colour(nav % (user_name, collection[flag]), colour='green')


def redis_error():
    remind = u"""
    您此次会话未能成功保存不能免密码登录机器,可以通过密码登录后端机器,另外请将此事告知Jumper管理员!
    \r
"""
    return get_colour(remind)


def date_handler(obj):
    if isinstance(obj, datetime):
        return str(obj)


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


def jumper_status():
    return {
        '1': u'正在连接到后端',
        '2': u'等待密码',
        '3': u'和后端管理建立成功'
    }


def get_user_ps1(login_name):
    return get_colour('[{0}@Jumper]# '.format(login_name), colour='yellow')


def check_user(user_name):
    """ 从jumper数据库从获取用户信息 """
    user = Async.get_user(dict(login_name=user_name))
    if user:
        if int(user['lock_times']) >= 6:
            Notice(u'您的Jumper账号最近连续输错密码超过6次, 已锁定, 解锁请前往 http://ops.sankuai.com/workflow/#/start/jumper-unlock'.format(
                    user_name), user['email'])
            return user, 4  # 锁定用户
        elif user['enable']:
            return user, 0  # 正常用户
        else:
            Notice(u'您的Jumper账号显示您已离职, 请不要继续尝试!', user['email'])
            return None, 3  # 离职用户
    elif isinstance(user, list):
        user = get_user_auth(user_name)
        if user:
            Notice(
                    u'您的mis账号: {0} 尚未开通Jumper登录权限, 详见wiki: https://wiki.sankuai.com/pages/viewpage.action?pageId=624539419'.format(
                            user_name), user['email'])
            return None, 2  # 未注册终端权限用户
        else:
            return None, 1  # 非法用户
    else:
        Notice(u'用户({0})登录跳板机时遇到接口出错，请管理员排查接口稳定性({1})'.format(user_name, socket.gethostname()), config['admin_user'])
        return None, 5  # 接口出错


def get_user_auth(user_name):
    """ 从企业获取员工信息 """
    try:
        user_info = http_client(url=config['ops_auth'].format(user_name), timeout=10).json().get('user')
        return dict(
                number=user_info['employeeId'],
                login_name=user_info['ad'],
                name=user_info['employeeName'],
                organization=user_info['organizationName'],
                source=user_info['source'],
                email=user_info['email'],
                mobile=user_info['mobileNo']
        )
    except Exception, e:
        logging.info(u'从企业系统获取用户信息({0})失败: {1}'.format(user_name, str(e)))


def get_ip_address(host):
    try:
        socket.inet_aton(host)
        return host
    except socket.error:
        try:
            ip = socket.gethostbyname(host)
            return ip
        except gaierror:
            return get_ip(host)


def alive_port(host, port):
    s = socket.socket()
    s.settimeout(0.5)
    con = (host, port)
    try:
        s.connect(con)
    except socket.error:
        return False
    return True


def get_ip(host):
    ip = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if ip.match(host):
        return False
    else:
        host = '.'.join([i for i in host.split('.') if i])  # 去除行位.号
        host_ip = Async.host_ip(host)
        return host_ip if host_ip else None


def permission_deny(user_info, ssh_option, option='check'):
    user_name = user_info['login_name']
    host_name = ssh_option['host_name']
    host_ip = get_ip_address(host_name)
    temp = '{0}:{1}'.format(user_name, host_ip)
    if option == 'delete':
        return Async.del_permission(temp)
    return Async.get_permission(temp)


def backup_pid(pid_file):
    if os.path.exists(pid_file):
        shutil.copy(pid_file, "/tmp/jumper-service.pid")


def rollback_pid(pid_file):
    if os.path.exists("/tmp/jumper-service.pid"):
        shutil.copy("/tmp/jumper-service.pid", pid_file)


def get_traceback():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback_details = dict(
            filename=exc_traceback.tb_frame.f_code.co_filename,
            lineno=exc_traceback.tb_lineno,
            name=exc_traceback.tb_frame.f_code.co_name,
            type=exc_type.__name__,
            message=exc_value.message
    )
    return u"""Traceback (most recent call last):
    File "{filename},
    line "{lineno}", in {name}
    {type}: {message}
    """.format(**traceback_details)


class Ssh:
    def __init__(self):
        self.url = config['google_auth_api']
        self.app_id = str(config['app_id'])
        self.sha_key = str(config['sha_key'])
        self.client_ua = str(config['client_ua'])
        self.timestamp = str(int(time.time()))
        self.client_ip = nic.ifaddresses(config['network_interface'])[2][0]['addr']

    @staticmethod
    def decode_public_key(db_key, client_key):
        try:
            local_key = db_key.split()[1]
        except IndexError:
            local_key = db_key
        if paramiko.RSAKey(data=decodebytes(local_key)) == client_key:
            return True
        if paramiko.DSSKey(data=decodebytes(local_key)) == client_key:
            return True
        if paramiko.ECDSAKey(data=decodebytes(local_key)) == client_key:
            return True

    @staticmethod
    def send_code(user_info, code, client_ip):
        message = u'''验证码:{0} (仅限本次登录使用), 欢迎登录新美大跳板机, 请勿将动态码告知他人,
如非本人({1})操作请对比你电脑IP和登录来源IP({2}) '''
        try:
            Notice(message.format(code, user_info['login_name'], client_ip), user_info['email'])
            logging.debug(u'\t调用大象接口, 发送动态密钥成功: {0} - {1}'.format(user_info['login_name'], code))
        except Exception as e:
            logging.error(u'\t调用大象接口, 发送动态密钥失败: {0} - {1}'.format(user_info['login_name'], str(e)))

    def check_code(self, user_name, code):
        raw_data = user_name + code + self.app_id + self.client_ip + self.client_ua + self.timestamp
        h = hmac.new(self.sha_key, raw_data, sha1)
        sign = b64encode(h.digest())
        payload = dict(
                user=user_name,
                otp=code,
                appid=self.app_id,
                clientip=self.client_ip,
                clientua=self.client_ua,
                sign=sign,
                timestamp=self.timestamp
        )
        try:
            result = requests.post(url=self.url, data=payload, verify=False).json()
        except Exception as e:
            logging.error(u'\t大象动态密码验证 失败 {0} - {1}'.format(user_name, str(e)))
        else:
            logging.info(u'\t大象动态密码验证 成功')
            return result['data'] == 'ok'


def check_unicode(cmd):
    try:
        json.dumps(cmd)
    except UnicodeDecodeError:
        return False
    return True
