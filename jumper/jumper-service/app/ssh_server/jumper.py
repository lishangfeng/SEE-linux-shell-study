# -*- coding:utf-8 -*-

import logging
import re
import threading
import time
from datetime import datetime

from termcolor import colored

from app.lib.command import ShellCommand
from app.lib.thread_pool import AsyncThread
from app.lib.utils import get_colour
from app.lib.utils import navigation
from app.ssh_server.init import commands_list
from app.ssh_server.init import config
from app.ssh_server.init import ssh_history
from app.terminal_control.terminal_control import TerminalControl
from app.terminal_player.pty_play import PtyPlay


class JumpServer:
    def __init__(self):
        self.poll = None
        self.stop = dict()              # ssh时线程间同步锁的变量
        self.play = dict()              # 播放屏幕录像
        self.status = dict()
        self.user_ps1 = None
        self.user_info = None
        self.sync_lock = None           # 根据ssh生成同步锁
        self.user_name = None
        self.proxy_server = None
        self.user_terminal = None
        self.backend_server = dict()
        self.connection_info = None
        self.user_navigation = None
        self.terminal_control = dict()

        # 命令解析
        self.command = dict()
        self.input = dict()

    def main(self):
        """
        channel的4种状态:
        0 --> 当前伪终端
        1 --> 正在连接后端机器
        2 --> 正在输入密码
        3 --> 已经和后端机器建立连接
        4 --> 正在播放频幕录像
        """
        while True:
            channel = self.poll.get_fd()
            if channel is False:
                self.proxy_server.close_transport()
                logging.warning(u'网络连接已断开, 退出循环')
                return
            else:
                data = channel.recv(391680)     # 24 * 16320(channel一次最大发送数据包)

            """ 判断是用户端还是后端channel """
            if channel in self.proxy_server.channel_list:   # proxy_server.channel
                if not self.status.get(channel):            # 初始化当前channel状态和channel伪终端
                    self.status[channel] = 0
                if not self.terminal_control.get(channel):
                    term = TerminalControl(self.user_ps1, self.user_name, self.user_terminal, channel, self)
                    self.terminal_control[channel] = term
                if channel.exit_status_ready():             # 异常退出终端, 网络断开 或 客户端 kill 了ssh进程
                    logging.warning(u'客户端异常关闭 [channel {0}] 通道'.format(channel.get_id()))
                    self.close(channel)
                    continue
            else:                                           # backend_server.channel
                self.transfer(channel, data)
                continue

            """ 通道状态 """
            if self.status[channel] == 1:                   # 连接后端机器中
                if data == '\x03':
                    self.status[channel] = 0                # ctrl+c 中断后端机器连接, 进入伪终端状态
                    self.stop[self.sync_lock].set()         # ctrl + c 增加计数器
                    channel.sendall('^C\r\n')
                    channel.sendall(self.user_ps1)
                else:
                    channel.sendall(data)
                continue
            elif self.status[channel] == 2:                 # 正在输入密码
                self.terminal_control[channel].password_send.send(data)
                continue
            elif self.status[channel] == 3:                 # 后端建立连接成功
                if not len(data):                           # fix 当用户直接x掉终端窗口, 会无限循环的收到一个size为0的数据
                    self.close(channel)
                    if self.proxy_server.session_type == 0:
                        return
                    elif self.proxy_server.session_type == 1 and len(self.proxy_server.channel_list) == 0:
                        return
                else:
                    self.transfer(channel, data)
                continue
            elif self.status[channel] == 4:                 # 正在播放频幕录像
                if data == '\x03':                          # 终止播放
                    self.play[channel].stop = True
                    self.status[channel] = 0
                    channel.sendall('^C\r\n')
                    channel.sendall(self.user_ps1)
                elif data == ' ':                           # 暂停播放
                    if self.play[channel].pause:
                        channel.sendall('\x08\x1b[K' * 13)
                        self.play[channel].pause = False
                        logging.info(u'取消暂停 {0}'.format(self.play[channel].play_uuid))
                    else:
                        self.play[channel].pause = True
                        channel.sendall(colored(u' ----暂停----', color='red'))
                        logging.info(u'暂停播放 {0}'.format(self.play[channel].play_uuid))
                elif data == '\x1b[C':                      # -> 快进5秒
                    self.play[channel].forward = True
                elif data == '\x1b[D':                      # <- 后退5秒
                    self.play[channel].backward = True
                continue

            # print '伪终端状态: data-->', data.encode("string-escape")
            """ 终端处理 """
            self.terminal_control[channel].process(data)
            if self.terminal_control[channel].logout:
                self.close(channel)
                if self.proxy_server.session_type == 0:
                    return
                elif self.proxy_server.session_type == 1 and len(self.proxy_server.channel_list) == 0:
                    return
                else:
                    continue

            elif self.terminal_control[channel].control_string:
                for control_string in self.terminal_control[channel].control_string:
                    channel.sendall(control_string)
                self.terminal_control[channel].control_string = list()

            elif not channel.get_transport().is_active():   # 伪终端非正常关闭时
                self.close()
                return
            else:
                channel.sendall(data)

            if self.terminal_control[channel].enter:
                command = self.terminal_control[channel].command.strip()
                self.terminal_control[channel].enter = False
                self.terminal_control[channel].command = ''
                # logging.debug(u'{0} -> {1}'.format(self.user_name, command.encode("string-escape")))
            else:
                continue

            # 密码过期, 密码重置 强制用户修改密码
            if self.proxy_server.password_expired or self.proxy_server.password_reset:
                self.proxy_server.password_retry += 1
                if self.proxy_server.password_retry > 2:
                    self.close()
                command = 'p'

            # !1 调用历史命令, r$d调用登录历史
            if re.match(r'!\d+$', command):
                number = eval(command.split('!')[1])
                if 0 < number <= len(commands_list):
                    command = commands_list[-number].keys()[0]
                else:
                    channel.sendall(get_colour(u'命令下标{0}不在历史记录范围, 请输入history检查\r\n'.format(number)))
                    channel.sendall(self.user_ps1)
                    continue
            elif re.match(r'!\S+', command):
                search_string = command.split()[0][1:]
                for x in commands_list[::-1]:
                    if x.keys()[0].find(search_string) != -1:
                        command = x.keys()[0]
                        break
            elif re.match(r'r\d+$', command):
                number = eval(command.split('r')[1])
                if 0 < number <= len(ssh_history):
                    _history = ssh_history[number - 1]
                    hostname = _history['host_name']
                    host_port = _history['host_port']
                    login_name = _history.get('login_name') or _history['user_name']
                    command = 'ssh {0}@{1} -p{2}'.format(login_name, hostname, host_port)
                else:
                    channel.sendall(get_colour(u'快捷键r{0} 不在登录历史记录范围, 请输入r 检查\r\n'.format(number)))
                    channel.sendall(self.user_ps1)
                    continue
            if command.strip():
                try:
                    logging.info(u'用户伪终端输入命令: {0}'.format(command))
                except UnicodeDecodeError:
                    logging.warning(u'用户伪终端输入命令解码有问题')
            """ 命令处理 """
            if command in ['h', 'H', 'help']:
                channel.sendall(navigation(self.user_info))
            elif command in ['q', 'exit']:
                self.close(channel)
                if self.proxy_server.session_type == 0:
                    return
                elif self.proxy_server.session_type == 1 and len(self.proxy_server.channel_list) == 0:
                    return
                else:
                    continue
            elif command == 'clear':
                channel.sendall('\x1b[H\x1b[2J{0}'.format(self.user_ps1))
                continue
            elif command in ['E', 'e']:
                channel.sendall(u'功能正在开发中...\r\n')
            elif command.startswith('telnet'):
                channel.sendall(u'telnet 协议支持正在开发中...\r\n')
            elif command in ['i', 'info', 'information']:
                ShellCommand.info(channel, self.connection_info)
            elif command == 'config' or command.startswith('config'):
                if self.user_info['role'] in config['admin_role']:
                    ShellCommand.config(channel)
                else:
                    channel.sendall(get_colour(u'嘿嘿，您还没有权限操作此命令.\r\n'))
            elif command.startswith('id '):
                ShellCommand.user_id(command, channel, self.user_info)
            elif command in ['U', 'u', 'user', 'id']:
                ShellCommand.user_info(channel, self.user_info)
            elif command in ['r', 'R']:
                ShellCommand.r(channel, self.user_info['uid'])
            elif command in ['P', 'p', 'password']:
                terminal = self.terminal_control[channel]
                kwargs = dict(status=self.status, terminal=terminal, channel=channel, user_info=self.user_info,
                              jumper=self)
                AsyncThread(target=ShellCommand.password, **kwargs)
                continue
            elif command in ['ssh'] or command.startswith('ssh'):
                self.sync_lock = '{0}_{1}'.format(channel.get_id(), int(time.time()))
                self.stop[self.sync_lock] = threading.Event()
                ShellCommand.ssh(self, channel, command, self.sync_lock)
                continue
            elif command == 'ping' or command.startswith('ping'):
                terminal = self.terminal_control[channel]
                kwargs = dict(terminal=terminal, command=command, channel=channel, jumper=self)
                AsyncThread(target=ShellCommand.ping, **kwargs)
                continue
            elif command.startswith('kinit'):
                terminal = self.terminal_control[channel]
                kwargs = dict(status=self.status, terminal=terminal, channel=channel, user_info=self.user_info,
                              proxy_server=self.proxy_server)
                AsyncThread(target=ShellCommand.kinit, **kwargs)
                continue
            elif command.startswith('getapp'):
                ShellCommand.getapp(channel, command)
            elif command.startswith('gethost'):
                ShellCommand.gethost(channel, command)
            elif command.startswith('pssh') or command.startswith('plog'):
                kwarg = dict(jumper=self, terminal=self.terminal_control[channel], channel=channel, command=command)
                AsyncThread(target=ShellCommand.pssh, **kwarg)
                continue
            elif command.startswith('history'):
                ShellCommand.history(command, channel, self.terminal_control.get(channel))
            elif command.startswith('play'):
                self.play[channel] = PtyPlay(jumper=self, channel=channel)
                self.play[channel].main(command)
                continue
            elif command:
                channel.sendall(get_colour(u'命令 {0} 不存在, 键入 H 查看帮助信息\r\n'.format(command)))
            channel.sendall(self.user_ps1)

    def proxy(self, proxy_server):
        self.poll = proxy_server.poll
        self.connection_info = proxy_server.connection_info
        self.user_ps1 = proxy_server.user_ps1
        self.user_info = proxy_server.user_info
        self.user_name = proxy_server.user_name
        self.user_terminal = proxy_server.terminal
        self.user_navigation = proxy_server.user_navigation
        self.proxy_server = proxy_server

    def close(self, channel=None):
        # 在多路复用情况下断开tcp连接;  关闭所有通道
        if not channel:
            logging.info(u'{0} 用户断开连接, 关闭所有通道'.format(self.user_name))
            for backend_server in self.backend_server.values():
                self.poll.unregister(backend_server.channel)
                backend_server.close()
            self.proxy_server.close()
            ShellCommand.ping_close(None)
            return True

        # 正常情况或多路复用单个channel关闭;  1:关闭通道对应后端机器channel   2:清理通道状态    3:清理终端term  4:关闭指定通道
        if self.backend_server.get(channel):
            backend_server = self.backend_server.get(channel)
            self.backend_server.pop(channel)
            self.poll.unregister(backend_server.channel)
            backend_server.close()
            logging.info(u'{0} 用户断开后端链接: {1}'.format(self.user_name, backend_server.host_name))
        if self.status.get(channel):
            self.status.pop(channel)
        if self.terminal_control.get(channel):
            self.terminal_control.pop(channel)
        if self.command.get(channel):
            self.command.pop(channel)
        if self.input.get(channel):
            self.input.pop(channel)

        ShellCommand.ping_close(channel.get_id())
        self.proxy_server.close(channel)
        logging.info(u'{0} 用户会话窗口关闭, 关闭 {1} 通道'.format(self.user_name, channel.get_id()))

    def transfer(self, channel, data):
        try:
            if channel.exit_status_ready():     # 用户主动退出
                for proxy_channel, backend_server in self.backend_server.items():
                    if channel == backend_server.channel:
                        self.poll.unregister(backend_server.channel)
                        backend_server.close()
                        self.status[proxy_channel] = 0
                        self.backend_server.pop(proxy_channel)
                        self.proxy_server.backend_server.pop(proxy_channel)
                        self.command[proxy_channel] = ''
                        self.input[proxy_channel] = False
                        proxy_channel.sendall('\r\n')
                        proxy_channel.sendall(self.user_ps1)
            elif channel in self.proxy_server.channel_list:                 # 用户发送给后端服务器命令
                self.input[channel] = True
                if data == '\r':
                    self.input[channel] = False
                    if self.command.get(channel):
                        self.backend_server[channel].cmd_recorder.pool.add_task((self.command[channel], datetime.now()))

                    self.command[channel] = ''
                elif data == '\x03':
                    self.input[channel] = False
                    self.command[channel] = ''
                self.backend_server[channel].channel.sendall(data)
            else:                                                           # 后端服务器返回给用户输出
                for proxy_channel, backend_server in self.backend_server.items():
                    if channel == backend_server.channel:
                        backend_server.pty_recorder.pool.add_task(data)     # 屏幕录像
                        if self.input.get(proxy_channel):
                            self.process_command(proxy_channel, data)
                        proxy_channel.sendall(data)
        except Exception as e:
            logging.warning(u'后端返回数据, 检查到用户到伪终端网络断开, 退出终端: {0}'.format(str(e)))
            self.close()

    def process_command(self, channel, data):
        if not self.command.get(channel):
            self.command[channel] = ''
        if len(self.command[channel]) < 1000:   # 过长命令忽略
            self.command[channel] += data
