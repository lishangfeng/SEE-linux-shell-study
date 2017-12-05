# -*- coding:utf-8 -*-

import copy
import logging
import os
from datetime import datetime
from threading import Thread

from app.lib.async import Async
from app.lib.error_define import ExitError
from app.lib.error_define import exception_wrapper
from app.lib.utils import get_colour
from app.lib.utils import permission_deny
from app.ssh_server.backend_server import BackendServer
from app.ssh_server.init import config
from app.ssh_server.init import ssh_history


class GetBackend(Thread):
    def __init__(self, ssh_option, jumper, proxy_channel, session_expired, sync_lock):
        Thread.__init__(self)
        self.session_expired = session_expired
        self.daemon = True
        self.ssh_option = ssh_option
        self.jumper = jumper
        self.proxy_channel = proxy_channel
        self.sync_lock = sync_lock

        self.user_terminal = self.jumper.user_terminal.get(proxy_channel)
        self.terminal_control = self.jumper.terminal_control[proxy_channel]
        self.status = self.jumper.status
        self.stop = self.jumper.stop
        self.user_name = jumper.user_name
        self.user_info = jumper.user_info
        self.backend_server = None
        self.start()

    @exception_wrapper
    def run(self):
        if not self.ssh_option.get('user_name') or self.ssh_option.get('user_name') == self.user_name:
            if not self.session_expired:
                user_info = copy.deepcopy(self.user_info)
                user_info['password'] = config['uuid']
            else:
                self.session_expired = 1
                user_info = dict(login_name=self.user_name)
                if not self.get_password(user_info):
                    return False
        else:
            user_info = dict(login_name=self.ssh_option.get('user_name'))
            if not self.get_password(user_info):
                return False

        self.backend_server = BackendServer(self.user_name, host_info=self.ssh_option, terminal=self.user_terminal)
        connect_result = self.backend_server.connect()
        failure_remind = get_colour(u'登录服务器失败, 原因--> {0}\r\n')
        if connect_result != 'ok':
            if self.status[self.proxy_channel] != 0:
                if connect_result == 1:
                    remind = u'[主机名无法解析]'
                elif connect_result == 2:
                    remind = u'[主机端口连接超时, 机器挂了?]'
                elif connect_result == 3:
                    remind = u'[ssh端口拒绝访问: {0}]'.format(self.ssh_option['host_port'])
                elif connect_result == 4:
                    remind = u'[协议错误, ssh进程僵死或非ssh协议端口({0})]'.format(self.ssh_option['host_port'])
                else:
                    remind = u'[未分类错误: {0}]'.format(connect_result)
                try:
                    self.send_msg(failure_remind.format(remind))
                    self.send_msg(self.jumper.user_ps1)
                    self.status[self.proxy_channel] = 0
                except Exception as e:
                    logging.warning(u'终端连接: {0}'.format(str(e)))
            return False

        i = 1
        while True:
            if self.backend_server.auth(user_name=user_info['login_name'], password=user_info['password']):
                break
            elif self.status[self.proxy_channel] == 0:
                logging.info(u'^C中断连接')
                self.backend_server.close()
                return False
            elif permission_deny(user_info, self.ssh_option):
                permission_deny(user_info, self.ssh_option, 'delete')
                self.send_msg(get_colour(u'您没有权限登录该机器! 请联系主机对应的RD负责人或者SRE负责人.\r\n'))
                self.send_msg(self.jumper.user_ps1)
                self.backend_server.close()
                self.status[self.proxy_channel] = 0
                return False
            else:
                logging.warning(u'密码错误登录失败 {0}'.format(self.ssh_option['host_name']))
            if i >= 3:
                self.send_msg(get_colour(u'请联系主机SRE负责人排查目标机器配置.\r\n'))
                self.send_msg(self.jumper.user_ps1)
                self.backend_server.close()
                self.status[self.proxy_channel] = 0
                return False
            else:
                i += 1
            if not self.get_password(user_info):
                return False

        if not self.backend_server.start():
            try:
                self.send_msg(u'[登录目标机器失败, 未知错误请联系SRE]')
                self.send_msg(self.jumper.user_ps1)
                self.status[self.proxy_channel] = 0
                self.backend_server.close()
            except Exception as e:
                logging.error(u'登录目标机器失败，未知错误 ==> {0}'.format(str(e)))
            return False
        if self.session_expired == 1:
            # 用户会话过期, 输入密码成功登录机器异步激活会话
            connection_info = dict(
                type='login_info',
                pid=os.getpid(),
                uuid=config['uuid'],
                session_type=self.jumper.proxy_server.session_type,
                user_id=self.jumper.user_info['uid'],
                login_name=self.jumper.user_info['login_name'],
                login_time=self.jumper.user_info['login_time'],
                name=self.jumper.user_info['name'],
                server_name=config['server_name'],
                client_ip=self.jumper.proxy_server.client_ip,
                client_port=self.jumper.proxy_server.client_port,
            )
            config['task'].add_task(Async.add_uuid, connection_info, self.jumper.user_info['source'])
        login_info = dict(
            jumper_name=config['server_name'],
            host_name=self.ssh_option['host_name'],
            host_port=self.ssh_option['host_port'],
            remote_ip=self.jumper.proxy_server.client_ip,
            remote_port=self.jumper.proxy_server.client_port,
            user_name=self.user_name,
            login_name=self.ssh_option.get('user_name') or self.user_name,
            user_uid=self.user_info['uid'],
            session_uuid=config['uuid'],
            login_uuid=self.backend_server.backend_uuid,
            login_time=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            channel_id=self.proxy_channel.get_id()
        )
        self.send_msg()
        config['task'].add_task(Async.put_login, login_info)
        config['task'].add_task(Async.heartbeat, self.jumper.proxy_server)

        self.backend_server.host_name = self.ssh_option['host_name']
        self.backend_server.proxy_channel = self.proxy_channel
        self.jumper.backend_server[self.proxy_channel] = self.backend_server

        self.jumper.proxy_server.backend_server[self.proxy_channel] = self.backend_server
        self.jumper.poll.register(self.backend_server.channel)

        self.status[self.proxy_channel] = 3
        host_port = self.ssh_option.get('host_port') or 22
        login_name = self.ssh_option.get('user_name') or self.user_name
        ssh_history.insert(0, dict(host_name=self.ssh_option['host_name'], host_port=host_port, login_name=login_name))
        del self.stop[self.sync_lock]

    def send_msg(self, msg=None):
        if self.stop[self.sync_lock].is_set():
            del self.stop[self.sync_lock]
            self.backend_server.close(True)
            raise ExitError
        if msg:
            self.proxy_channel.sendall(msg)

    def get_password(self, user_info):
        message = u'{0}@{1} "s Password: '.format(user_info['login_name'], self.ssh_option['host_name'])
        logging.info(u'准备等待密码')
        user_info['password'] = self.terminal_control.get_password(self.status, self.proxy_channel, message)

        if user_info['password'] == '^C':
            self.status[self.proxy_channel] = 0
            self.proxy_channel.sendall('^C\r\n')
            self.proxy_channel.sendall(self.jumper.user_ps1)
            return False
        return user_info
