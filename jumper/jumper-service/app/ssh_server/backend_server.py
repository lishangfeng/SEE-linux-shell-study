# -*- coding:utf-8 -*-

import logging
import socket
import sys
from datetime import datetime
from uuid import uuid4

import paramiko

from app.command_parser.cmd_recorder import CmdRecorder
from app.lib.async import Async
from app.lib.utils import alive_port
from app.lib.utils import get_ip
from app.ssh_server.init import config
from app.terminal_recorder.pty_recorder import PtyRecorder


class BackendServer:
    def __init__(self, user_name, host_info, terminal=None):
        self.user_name = user_name
        self.terminal = terminal or dict()
        self.host_name = host_info.get('host_name')
        self.host_port = host_info.get('host_port')

        self.key = ''
        self.socket = None
        self.channel = None
        self.transport = None
        self.login_time = None
        self.login_name = ''
        self.pty_recorder = None
        self.cmd_recorder = None
        self.backend_uuid = str(uuid4())

    def start(self):
        try:
            self.open_session()
            self.get_pty()
            self.get_invoke_shell()
            return True
        except Exception as e:
            logging.error(u'请求交互式回话失败 {0}'.format(str(e)))

    def connect(self):
        """
        连接错误返回状态码
        ok: 连接后端成功
        1 : 主机无法解析
        2 : 主机端口连接超时
        3 : ssh端口错误
        4 : ssh协议错误
        未知错误直接返回错误信息
        :return:
        """
        try:
            logging.info('连接主机, {0}, {1}'.format(self.host_name, self.host_port))
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.host_name, self.host_port))
        except socket.gaierror:
            logging.warn(u'[{0}]主机名无法解析, 尝试匹配数据库主机fqdn'.format(self.host_name))
            host_ip = get_ip(self.host_name)
            if host_ip:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(10.0)
                try:
                    self.socket.connect((host_ip, self.host_port))
                except socket.gaierror:
                    logging.error(u'从数据库中获取的主机名无法解析, 检查host对应记录或当前jumper机器dns配置')
                    return 1
                except socket.error as e:
                    if str(e).find('Connection refused') != -1:
                        if self.host_port != 58422 and alive_port(self.host_name, 58422):
                            logging.warn('连接主机端口 {0} 失败, 尝试端口 58422'.format(self.host_port))
                            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.socket.settimeout(10.0)
                            self.host_port = 58422
                            try:
                                self.socket.connect((host_ip, self.host_port))
                            except socket.error:
                                logging.warning(u'连接端口58422超时 {0}'.format(self.host_name))
                                return 3
                        else:
                            return 3
                    elif str(e).find('timed out') != -1:
                        logging.warn(u'连接主机超时 {0}:{1}'.format(self.host_name, self.host_port))
                        return 2
                    else:
                        return str(e)
            else:
                return 1
        except socket.timeout:
            logging.warn(u'连接主机超时 {0}:{1}'.format(self.host_name, self.host_port))
            return 2
        except socket.error as e:
            if str(e).find('Connection refused') != -1:
                if self.host_port != 58422 and alive_port(self.host_name, 58422):
                    logging.warn('连接主机端口 {0} 失败, 尝试端口 58422'.format(self.host_port))
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.settimeout(10.0)
                    self.host_port = 58422
                    try:
                        self.socket.connect((self.host_name, self.host_port))
                    except socket.error:
                        logging.warning(u'连接端口58422超时 {0}'.format(self.host_name))
                        return 3
                else:
                    return 3
            elif str(e).find('timed out') != -1:
                logging.warn(u'连接主机超时 {0}:{1}'.format(self.host_name, self.host_port))
                return 2
            else:
                return str(e)

        try:
            self.transport = paramiko.Transport(self.socket)
            self.transport.start_client()
            return 'ok'
        except paramiko.SSHException as e:
            logging.warning(u'连接到服务器失败: {0}'.format(str(e)))
            if str(e).find('SSH protocol banner'):
                return 4
            return str(e)

    def auth(self, user_name, password):
        if not user_name or not password:
            return False
        try:
            logging.info(u'验证密码: {0}'.format(user_name))
            self.transport.auth_password(username=user_name, password=password)
            self.login_name = user_name
            return True
        except (paramiko.AuthenticationException, paramiko.SSHException):
            logging.warning(u'认证失败 {0} -> {1}'.format(user_name, self.host_name))

    def read_public_key(self, key):
        if 'BEGIN RSA PRIVATE KEY' in key:
            self.key = paramiko.RSAKey(filename=key)
        elif 'BEGIN DSA PRIVATE KEY' in key:
            self.key = paramiko.DSSKey(filename=key)
        else:
            logging.warning(u'密钥类型不对,目前只支持 RSA/DSA 两种格式')

    def open_session(self):
        self.channel = self.transport.open_session()

    def get_pty(self):
        self.channel.get_pty(**self.terminal)
        return True

    def get_invoke_shell(self):
        self.channel.invoke_shell()
        self.pty_recorder = PtyRecorder(self)       # 初始化录像
        self.cmd_recorder = CmdRecorder(self)       # 初始化命令记录

    def close(self, sync_lock=None):
        try:
            if self.channel:
                self.channel.close()
                if not sync_lock:
                    config['task'].add_task(Async.update_login, self.backend_uuid, logout_time=datetime.now())
            self.transport.close()
            self.pty_recorder.pool.add_task(sys.exit)
            self.cmd_recorder.pool.add_task(sys.exit)
            config['task'].add_task(self.pty_recorder.wait_completion)
            config['task'].add_task(self.cmd_recorder.wait_completion)
        except AttributeError:
            pass

    def send(self, data):
        self.channel.sendall(data)

    def receive(self, buf=10240):
        return self.channel.recv(buf)
