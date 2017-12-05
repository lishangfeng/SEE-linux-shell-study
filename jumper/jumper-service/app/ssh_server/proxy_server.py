# -*- coding:utf-8 -*-

import json
import logging
import os
import re
import socket
import threading
import uuid
from datetime import datetime

import paramiko
from termcolor import colored

from app.lib.async import Async
from app.lib.password import Password
from app.lib.utils import Ssh
from app.lib.utils import check_user
from app.lib.utils import get_colour
from app.lib.utils import get_user_ps1
from app.lib.utils import invalid_navigation
from app.lib.utils import navigation
from app.lib.utils import redis_error
from app.ssh_server.init import command_pids
from app.ssh_server.init import commands_list
from app.ssh_server.init import config
from app.ssh_server.poll import Poll
from app.ssh_server.transport import Transport


class ProxyServer(paramiko.ServerInterface):
    def __init__(self, client_socket, client_ip, client_port, server_name=socket.gethostname()):
        self.event = threading.Event()
        self.socket = client_socket
        self.server_name = server_name
        self.client_ip = client_ip
        self.client_port = client_port
        self.backend_server = dict()
        self.terminal = dict()
        self.user_info = dict()
        self.user_name = None
        self.channel_list = list()
        self.transport = None
        self.code = None
        self.invalid_user = False
        self.user_navigation = None
        self.user_ps1 = None
        self.connection_info = None
        self.poll = Poll()
        self.password_expired = False
        self.password_reset = False
        self.password_retry = 0
        self.redis_error = False
        self.lock = threading.Lock()
        self.recorder_list = list()
        self.clean_session = False      # 断开socket清理会话标记, 只需清理一次
        self.session_type = None        # 会话模式, 0:关闭复用, 1: 前台复用, 2: 后台复用

    def get_allowed_auths(self, user_name):
        self.user_name = user_name
        if not self.user_info:
            self.user_info, self.invalid_user = check_user(user_name)
            if self.user_info and not self.invalid_user:
                logging.info(u'{0}, 获取用户信息成功'.format(user_name))
            else:
                logging.info(u'用户{0}非法或账号锁定,无法登录,提示用户然后关闭连接'.format(user_name))
                return 'publickey'

        # 如果对方有公钥在服务端, 特殊角色可跳过动态认证
        if self.user_info.get('role') in config['admin_role']:
            logging.info(u'用户[{0}]属于管理员[{1}]角色:{2}'.format(user_name, config['admin_role'], self.user_info.get('role')))
            if config.get('dynamic_password'):
                return 'publickey,keyboard-interactive'
            else:
                return 'publickey,password'
        elif config.get('dynamic_password'):
            logging.info(u'用户[{0}]属于普通角色[{1}]'.format(user_name, self.user_info.get('role')))
            return 'keyboard-interactive, password'
        else:
            return 'password'

    def check_auth_interactive(self, user_name, submethods):
        if config.get('dynamic_password') and config.get('dx_code'):
            if not self.code:
                self.code = ''.join([i for i in str(uuid.uuid4()) if re.match(r'\d', i)][:6])
                Ssh.send_code(self.user_info, self.code, self.client_ip)

        # 兼容手机termius客户端登录
        self.user_name = user_name
        if not self.user_info:
            self.user_info, self.invalid_user = check_user(user_name)
            if not self.user_info:
                return paramiko.AUTH_FAILED
        wiki = colored(u'帮助文档 -> https://wiki.sankuai.com/pages/viewpage.action?pageId=624539419\r\n', color='green')
        password_prompt = [wiki + 'Password: ', 'verification code: ']
        return paramiko.InteractiveQuery('', '', *[(i, False) for i in password_prompt])

    def check_auth_interactive_response(self, responses):
        user_name = self.user_name
        if config.get('dynamic_password'):
            password, code = responses[0], responses[1]
            if len(password) < 8:
                logging.warning(u'{0}, 提交的密码总长度太短,验证失败,密码+code长度需要大于12.'.format(self.user_name))
                return paramiko.AUTH_FAILED
        else:
            password, code = responses[0], None

        try:
            if Password.check_password(self.user_info, password, login=True):
                if code == self.code:                   # 内存code比对
                    logging.info(u'随机动态码验证成功!')
                    return paramiko.AUTH_SUCCESSFUL
                elif Ssh().check_code(user_name, code):  # 大象code比对
                    return paramiko.AUTH_SUCCESSFUL
                else:
                    logging.warning(u'随机动态码验证失败!')
                    return paramiko.AUTH_FAILED
            logging.warning(u'{0}, 验证密码失败!'.format(self.user_name))
        except Exception as e:
            # 兼容手机termius客户端登录
            logging.error(u'{0}, 手机客户端用户非法, 登录失败, 错误:{1}'.format(user_name, str(e)))
        return paramiko.AUTH_FAILED

    def check_auth_password(self, user_name, password):
        self.user_name = user_name
        # 兼容手机termius客户端登录
        if config.get('dynamic_password'):
            if self.invalid_user:
                return paramiko.AUTH_FAILED
            if len(password) == 36:
                if Password.check_onetime_password(password):
                    logging.info(u'websocket密码验证成功!')
                    return paramiko.AUTH_SUCCESSFUL
                logging.warning(u'websocket密码验证失败!')
                return paramiko.AUTH_FAILED
            password, code = password[:-6], password[-6:]
            if Password.check_password(self.user_info, password, login=True):
                if code == self.code:                   # 内存code比对
                    logging.info(u'随机动态码验证成功!')
                    return paramiko.AUTH_SUCCESSFUL
                elif Ssh().check_code(user_name, code):  # 大象code比对
                    return paramiko.AUTH_SUCCESSFUL
                else:
                    logging.warning(u'随机动态码验证失败!')
                    return paramiko.AUTH_FAILED
            logging.warning(u'{0}, 类手机客户端termius验证密码失败!'.format(self.user_name))
            return paramiko.AUTH_FAILED
        else:
            if self.invalid_user:
                return paramiko.AUTH_FAILED
            if user_name == self.user_info['login_name']:
                if Password.check_password(self.user_info, password, login=True):
                    logging.info(u'{0}, 验证密码成功'.format(user_name))
                    return paramiko.AUTH_SUCCESSFUL
                elif len(password) == 36:
                    if Password.check_onetime_password(password):
                        logging.info(u'websocket密码验证成功!')
                        return paramiko.AUTH_SUCCESSFUL
                    logging.warning(u'websocket密码验证失败!')
                    return paramiko.AUTH_FAILED
                logging.warning(u'{0}, 验证密码失败'.format(user_name))
            else:
                logging.warning(u'账号信息错误{0}: {1}'.format(user_name, self.user_info['login_name']))
                return paramiko.AUTH_FAILED
            return paramiko.AUTH_FAILED

    def check_auth_publickey(self, user_name, key):
        if self.invalid_user:
            return paramiko.AUTH_SUCCESSFUL
        if self.user_info.get('public_key'):
            try:
                if Ssh.decode_public_key(self.user_info['public_key'], key):
                    logging.info(u'{0}, key登录成功'.format(user_name))
                    return paramiko.AUTH_SUCCESSFUL
            except Exception as e:
                logging.warning(u'{0}, key登录失败, {1}'.format(user_name, str(e)))
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chan_id):
        if kind == 'session':
            self.user_info, self.invalid_user = check_user(self.user_name)
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        if self.invalid_user:
            channel.sendall(invalid_navigation(self.user_name, self.invalid_user))
            self.transport.close()  # 如果不断开, 在tcp复用情况下会有漏洞
            return False

        if not self.channel_list:
            if channel.remote_chanid == 0:
                self.session_type = 0
            elif channel.remote_chanid % 2:
                self.session_type = 1
            else:
                self.session_type = 2
            self.user_navigation = navigation(self.user_info)
            self.user_ps1 = get_user_ps1(self.user_name)
            self.get_connection_info()
            self.event.set()

        self.poll.register(channel)
        self.channel_list.append(channel)
        # 密码过期检查
        remind = Password.password_remind(self.user_info)
        if remind:
            if remind[0] == 0:
                channel.sendall(get_colour(remind[1]))
                self.password_expired = True
            elif remind[0] == 1:
                channel.sendall(get_colour(remind[1]))
                self.password_reset = True
            elif remind[0] == 2:
                channel.sendall(self.user_navigation)
                channel.sendall(get_colour(remind[1]))
                if self.redis_error:
                    channel.sendall(redis_error())
                channel.sendall(self.user_ps1)
        else:
            channel.sendall(self.user_navigation)
            if self.redis_error:
                channel.sendall(redis_error())
            channel.sendall(self.user_ps1)

        config['task'].add_task(Async.heartbeat, self)
        config['task'].add_task(Async.get_recorder, self)
        command_pids['channel_{0}'.format(channel.get_id())] = list()
        logging.info(u'建立交互式回话成功: {0}'.format(channel.get_id()))
        return True

    def check_channel_exec_request(self, channel, command):
        logging.warning(u'不允许远程执行命令')
        return False

    def check_channel_pty_request(self, channel, term, width, height, width_pixels, height_pixels, modes):
        if not self.terminal.get(channel):
            self.terminal[channel] = dict()
        self.terminal[channel].update(
            term=term,
            width=width,
            height=height,
            width_pixels=width_pixels,
            height_pixels=height_pixels
        )
        return True

    def check_channel_window_change_request(self, channel, width, height, width_pixels, height_pixels):
        terminal = dict(width=width, height=height, width_pixels=width_pixels, height_pixels=height_pixels)
        self.terminal[channel].update(**terminal)
        if self.backend_server.get(channel):
            self.backend_server[channel].channel.resize_pty(**terminal)
        return True

    def check_channel_x11_request(self, channel, single_connection, auth_protocol, auth_cookie, screen_number):
        return True

    def start(self):
        if not self.get_transport():
            return False
        self.event.wait(300)
        if self.event.is_set():
            logging.info(u'{0} 用户登录成功'.format(self.user_name))
            self.user_info['login_time'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            config['task'].add_task(Async.get_command_history, self.user_name)
            config['task'].add_task(Async.get_login, self.user_info['uid'])
            config['task'].add_task(Async.update_user, self.user_info['uid'], self.user_info['login_time'])
            config['user_name'] = self.user_name
            return True
        logging.warning(u'{0}, 等待交互会话超时'.format(self.user_name))

    def get_transport(self):
        self.transport = Transport(self.socket)
        self.transport.set_keepalive(int(config['ssh_keep_alive']))
        self.transport.set_gss_host(socket.getfqdn(self.server_name))
        for key in config.get('ssh_server_keys'):
            self.transport.add_server_key(key)
            logging.debug(u'加载服务端密钥: {0}, {1}, {2}'.format(key.get_name(), key.size, key.get_base64()))
        else:
            logging.debug(u'尝试加载ssh协议')
            try:
                self.transport.start_server(server=self)
                self.poll.transport = self.transport
                return True
            except EOFError:
                logging.debug(u'断开连接 {0}'.format(self.client_ip))
            except paramiko.SSHException:
                logging.debug(u'SSH 错误 {0}'.format(self.client_ip))
            except Exception as e:
                logging.error(u'服务端异常, 出现未知错误: {0}'.format(str(e)))

    def get_connection_info(self):
        """ 记录uuid信息到redis """
        self.user_info['login_time'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.connection_info = dict(
            type='login_info',
            pid=os.getpid(),
            uuid=config['uuid'],
            user_id=self.user_info['uid'],
            login_name=self.user_info['login_name'],
            name=self.user_info['name'],
            server_name=config['server_name'],
            client_ip=self.client_ip,
            client_port=self.client_port,
            session_type=self.session_type,
            login_time=self.user_info['login_time']
        )
        if Async.add_uuid(self.connection_info, self.user_info['source']):
            logging.debug(u'缓存 session 成功: {0}'.format(json.dumps(self.connection_info)))
        else:
            self.redis_error = True
            logging.info(u'缓存 session 失败: {0}'.format(json.dumps(self.connection_info)))

    def close(self, channel=None):
        config['task'].add_task(Async.put_command_history, config['user_name'], commands_list)
        config['task'].add_task(Async.heartbeat, self)
        try:
            if not channel:                         # 未指定通道, 默认关闭所有通道
                for index in range(len(self.channel_list)):
                    channel_info = self.channel_list.pop()
                    self.poll.unregister(channel_info)
                    channel_info.close()
                self.close_transport()
                return

            if self.terminal.get(channel):          # 关闭指定通道
                self.terminal.pop(channel)
            self.channel_list.pop(self.channel_list.index(channel))
            self.poll.unregister(channel)
            channel.close()

            if self.session_type == 0:              # 根据回话类型, 是否关闭 transport
                self.close_transport()
                logging.info(u'session_type=0, 无连接复用, 关闭transport')
            elif self.session_type == 1 and len(self.channel_list) == 0:
                self.close_transport()
                logging.info(u'session_type=1, 前台复用模式, 已经关闭所有通道(channel), 关闭transport')
        except Exception as e:
            logging.warning(u'断开连接异常: {0}'.format(str(e)))

    def close_transport(self):
        self.lock.acquire()
        if self.transport.active:
            self.transport.close()
        if not self.clean_session:
            self.clean_session = True
            logging.info(u'清理会话, 关闭transport')
            config['task'].add_task(Async.clean_up, self.user_info['source'])
        self.lock.release()
