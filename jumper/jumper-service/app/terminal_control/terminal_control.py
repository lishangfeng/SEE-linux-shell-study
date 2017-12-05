# -*- coding:utf-8 -*-

import os
import re
from datetime import datetime
from multiprocessing import Pipe

from app.lib.utils import get_colour

from app.ssh_server.init import command_pids
from app.ssh_server.init import commands_list
from utils import retrieve_command
from utils import tab_command
from utils import tab_history
from utils import terminal_format

"""
    shell终端控制字符表

    \r      回车
    \t      tab
    \x1b    Esc
    \x01    ctrl+a 光标回行首
    \x02    ctrl+b 光标回退
    \x03    ctrl+c 取消
    \x04    ctrl+d 退出|不干啥|删除当前字符
    \x05    ctrl+e 光标移到行尾
    \x06    ctrl+f 光标向前移动
    \x07    删除字符
    \x7f    删除键
    \x10    ctrl+p 上一个
    \x0e    ctrl+n 下一个
    \x13    ctrl+s 冻结窗口
    \x12    Ctrl+r 搜索历史命令
    \x15    ctrl+u 删除光标至行首之间字符
    \x17    ctrl+w 删除光标前一个字符串
    \x19    ctrl+y 复制
    \x0b    ctrl+k 删除光标后字符
    \x0c    ctrl+l 清屏
    \x1b[A  向上方向键
    \x1b[B  向下方向键
    \x1b[C  -> 右方向键  \x1b[C
    \x1b[D  <- 左方向键  \x08
    \x1b[K  清屏
"""

"""
    shell下终端特殊字符意义
    \x1b[{n}P   删除n个字符串
    \x08        向行首光标移动一次
    \x1b[K      删除字符到光标位置
    \x1b[C      向行尾移动光标一次
    \x07        终端响铃
"""


class TerminalControl:
    """
    模拟bash终端
    控制字符处理
    支持bash常用快捷键等
    """
    def __init__(self, user_ps1, user_name, user_terminal, channel, jumper):
        self.channel = channel
        self.jumper = jumper
        self.user_ps1 = user_ps1
        self.user_name = user_name
        self.user_terminal = user_terminal
        self.command = ''
        # ctrl + y
        self.command_y = ''
        # 光标位置, 0表示末尾
        self.command_cursor = 0
        # 历史命令
        self.command_list = [str(i.keys()[0]) for i in commands_list] if commands_list else list()
        # 历史命令回溯游标
        self.command_index = len(self.command_list)
        # 控制字符输出
        self.control_string = list()
        # tab
        self.tab = False
        # get_password
        self.pause = False
        self.enter = False
        self.logout = False
        # ctrl + r
        self.retrieve = False
        self.retrieve_cmd = ''
        self.retrieve_index = 0
        self.retrieve_ps1 = "(reverse-i-search)`\': "

        pipe = Pipe()
        self.password_send = pipe[0]
        self.password_receive = pipe[1]

    def process(self, data):
        # 单引号(\\\'), 反斜线(\\\\)
        data_encode = data.encode("string-escape")
        spec_str = ["\\\'", "\\\\"]
        if (data_encode in spec_str or not data_encode.startswith('\\')) and data_encode.find('\\r') == -1:
            if self.retrieve:  # ctrl+R模式
                retrieve = retrieve_command(self.retrieve_cmd + data, self.command_list)
                if not retrieve:
                    self.control_string.append('\x07')
                    return
                _command, self.retrieve_index, _command_cursor = retrieve
                if not self.command:
                    # 初次检索
                    foo = "\x08\x08\x08{0}\': {1}{2}".format(data, _command, '\x08' * _command_cursor)
                    self.control_string.append(foo)
                    self.command = _command
                    self.retrieve_cmd += data
                    self.command_cursor = _command_cursor
                else:
                    # 不是初次检索
                    # 先把命令清除
                    self.control_string.append('\x08' * (len(self.command) - self.command_cursor + 3) + '\x1b[K')
                    # 添加新增的字符
                    foo = "{0}\': {1}{2}".format(data, _command, '\x08' * _command_cursor)
                    self.control_string.append(foo)
                    self.command = _command
                    self.retrieve_cmd += data
                    self.command_cursor = _command_cursor
                return

            if not self.command_cursor:
                # 多个字符,不支持
                if data_encode == "\\\'":
                    data = '\''
                elif data_encode == "\\\\":
                    data = '\\'
                self.command += data

            elif self.command_cursor:
                """ 插入命令 """
                if self.command[-self.command_cursor] == data:
                    if self.command_cursor - 1:
                        i = data + self.command[-int(self.command_cursor - 1):]
                        self.control_string.append(
                                '\x1b[C{0}{1}'.format(i, '\x08' * len(self.command[-self.command_cursor:]))
                        )
                        self.command = self.command[:-int(self.command_cursor - 1)] + i
                    else:
                        self.control_string.append('\x1b[C{0}{1}'.format(data, '\x08'))
                        self.command += data
                else:
                    i = data + self.command[-self.command_cursor:]
                    self.control_string.append('{0}{1}'.format(i, '\x08' * len(self.command[-self.command_cursor:])))
                    self.command = self.command[:-self.command_cursor] + i

        elif data_encode.find('\\r') != -1:
            """ 回车 """
            self.tab = False
            self.enter = True
            self.command_cursor = 0
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length + '\x1b[K')
                # 重置回原生用户提示
                self.control_string.append('\r' + self.user_ps1 + self.command)
                self.retrieve = False
                self.retrieve_cmd = ''
                self.retrieve_index = 0
            # 非手动回车
            if data_encode != '\\r':
                # 处理expect交互命令中的\t,\n控制字符 和 ' \特殊字符
                if not self.command:
                    for i in data_encode.split('\\r'):
                        if i.find('\\\\') or i.find('\\\''):
                            i = i.replace('\\\\', '\\')
                            i = i.replace('\\\'', '\'')
                        self.command += i.strip('\t').strip('\n')
                    self.control_string.append(self.command + '\r\n')
                # 处理复制命令时,含\t,\n控制字符 和 ' \特殊字符
                else:
                    for i in data_encode.split('\\r'):
                        if i.find('\\\\') or i.find('\\\''):
                            i = i.replace('\\\\', '\\')
                            i = i.replace('\\\'', '\'')
                        self.command += i.strip('\t').strip('\n')
                    self.control_string.append(data + '\r\n')
            # 手动回车
            else:
                self.control_string.append('\r\n')
            if self.command.strip() and not self.command.startswith('!'):
                # 过滤'\t','\n'控制字符
                if self.command.encode("string-escape").find('\\t') != -1 or \
                                    self.command.encode("string-escape").find('\\n') != -1:
                    self.command = self.command.replace('\t', ' ')
                    self.command = self.command.replace('\n', ' ')
                if not self.command_list:
                    self.command_list.append(self.command.strip())
                    commands_list.append(
                        {self.command.strip(): datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")})
                elif self.command_list[-1] != self.command:
                    self.command_list.append(self.command.strip())
                    commands_list.append(
                        {self.command.strip(): datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")})
                self.command_index = len(self.command_list)

        elif data == '\x04':
            """ control + D 退出, 或者删除字符 """
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                self.control_string.append('\r' + self.user_ps1 + self.command)
                # 光标放回
                self.control_string.append('\x08' * self.command_cursor)
                self.tab = False
                self.retrieve = False
                self.retrieve_index = 0
                self.retrieve_cmd = ''
            if self.command:
                left = self.command[:-self.command_cursor] if self.command_cursor else self.command
                right = self.command[-self.command_cursor:] if self.command_cursor else ''
                if right:
                    self.control_string.append('\x07\x1b[1P\x07')
                    self.command = left + right[1:]
                    self.command_cursor -= 1
                else:
                    return
            else:
                self.logout = True

        elif data == '\x03':
            """ control + C 终止当前任务 """
            if self.jumper.proxy_server.password_expired or self.jumper.proxy_server.password_reset:
                os.kill(os.getpid(), 15)
                self.jumper.close()
            if self.command:
                self.command = ''
                self.tab = False
                self.command_cursor = 0
                self.command_index = len(self.command_list)
                self.enter = True
                # 重置ctrl+r状态
                self.retrieve = False
                self.retrieve_cmd = ''
                self.retrieve_index = 0
                self.control_string.append('^C\r\n')
            else:
                self.retrieve = False
                self.retrieve_cmd = ''
                self.retrieve_index = 0
                self.control_string.append('^C\r\n' + self.user_ps1)

        elif data == '\x12':
            """ Ctrl + r 历史检索 """
            if self.retrieve:
                retrieve = retrieve_command(self.retrieve_cmd, self.command_list, index=self.retrieve_index)
                if not retrieve:
                    self.control_string.append('\x07')
                    return
                _command, self.retrieve_index, _command_cursor = retrieve
                if not self.command:
                    # 初次检索
                    foo = "\x08\x08\x08{0}\': {1}{2}".format(data, _command, '\x08' * _command_cursor)
                    self.command = _command
                    self.command_cursor = _command_cursor
                    self.control_string.append(foo)
                else:
                    # 非初次检索
                    # 先把命令清除
                    self.control_string.append('\x08' * (len(self.command) - self.command_cursor) + '\x1b[K')
                    # 添加新增的字符
                    self.control_string.append('{0}{1}'.format(_command, '\x08' * _command_cursor))
                    self.command = _command
                    self.command_cursor = _command_cursor
            else:
                self.retrieve = True
                self.command = ''
                # 清除用户提示
                self.control_string.append('{0}\x1b[K'.format('\x08' * len(self.command + self.user_ps1)))
                # 新的用户提示
                self.control_string.append('\r' + self.retrieve_ps1)

        elif data == '\x1b':
            """ ESC """
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                foo2 = '\r' + self.user_ps1 + self.command
                move_cursor = '\x08' * self.command_cursor
                self.control_string.append(foo2)
                self.control_string.append(move_cursor)
                self.retrieve = False
                self.retrieve_index = 0
                self.retrieve_cmd = ''
                return
            else:
                return
        elif data == '\t':
            """ tab 键 """
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                self.control_string.append('\r' + self.user_ps1 + self.command)
                self.retrieve = False
                self.retrieve_cmd = ''
                self.retrieve_index = 0
                self.command_cursor = 0
            if self.command.strip():
                # 命令补全
                if len(self.command.strip()) == len(self.command) and len(self.command.split()) == 1:
                    compared_command = tab_command(self.command)
                    # 搜索到一条匹配命令
                    if len(compared_command) == 1 or self.tab:
                        if not self.tab:
                            self.tab = True
                            if self.command_cursor:
                                self.control_string.append('\x1b[C' * self.command_cursor)
                            control = '{0}\x1b[K{1} '.format('\x08' * len(self.command), compared_command[0])
                            self.control_string.append(control)
                            self.command = compared_command[0] + ' '
                        else:
                            self.control_string.append('')
                    # 搜索到多条匹配命令
                    elif len(compared_command) > 1:
                        common_prefix = os.path.commonprefix(compared_command)
                        if common_prefix[len(self.command):]:
                            to_append_str = common_prefix[len(self.command):]
                            self.command += to_append_str
                            self.control_string.append(to_append_str)
                        else:
                            t_format = terminal_format(compared_command, self.user_terminal, self.channel)
                            self.control_string.append('\r\n' + t_format + self.user_ps1)
                            self.control_string.append(self.command)
                    # 未匹配结果, 不打印tab
                    else:
                        self.control_string.append('')
                # 命令参数补全
                else:
                    prefix, compared_history = tab_history(self.command, self.command_list)
                    if len(compared_history) == 1:
                        cmd_fix = compared_history[0] if not len(prefix) else compared_history[0].split(prefix)[1]
                        self.control_string.append(cmd_fix + ' ')
                        self.command += cmd_fix + ' '
                    elif len(compared_history) > 1:
                        common_prefix = os.path.commonprefix(compared_history)
                        if common_prefix[len(prefix):]:
                            to_append_str = common_prefix[len(prefix):]
                            self.command += to_append_str
                            self.control_string.append(to_append_str)
                        else:
                            t_format = terminal_format(compared_history, self.user_terminal, self.channel)
                            self.control_string.append('\r\n' + t_format + self.user_ps1)
                            self.control_string.append(self.command)
                    else:
                        self.control_string.append('')

                if self.command_cursor:
                    self.control_string.append('\x1b[C' * self.command_cursor)
                    self.command += ' '
                    self.control_string.append(' ')
            else:
                """ 无任何可见字符, 返回所有命令 """
                t_format = terminal_format(tab_command(self.command), self.user_terminal, self.channel)
                self.control_string.append(get_colour('\r\n当前终端支持的命令如下:\r\n', colour='green'))
                self.control_string.append('\r\n' + t_format + self.user_ps1)
                self.command = ''  # 置空命令, 避免删除ps1
            # tab 重置光标位置
            self.command_cursor = 0

        elif data == '\x01':
            """ control + A 移动光标到起始位 """
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                self.control_string.append('\r' + self.user_ps1 + self.command)
                # 光标放回
                self.control_string.append('\x08' * self.command_cursor)
                self.tab = False
                self.retrieve = False
                self.retrieve_index = 0
                self.retrieve_cmd = ''
            if self.command_cursor:
                self.control_string.append('{0}'.format('\x08' * int(len(self.command) - self.command_cursor)))
            else:
                self.control_string.append('{0}'.format('\x08' * len(self.command)))
            self.command_cursor = len(self.command)

        elif data == '\x05':
            """ control + E 移动光标到尾部 """
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                foo2 = '\r' + self.user_ps1 + self.command
                move_cursor = '\x08' * self.command_cursor
                self.control_string.append(foo2)
                self.control_string.append(move_cursor)
                self.retrieve = False
                self.retrieve_index = 0
                self.retrieve_cmd = ''
            if self.command_cursor == len(self.command):
                self.control_string.append('{0}'.format('\x1b[C' * len(self.command)))
            elif self.command_cursor != 0:
                self.control_string.append('{0}'.format('\x1b[C' * self.command_cursor))
            self.command_cursor = 0

        elif data in ['\x7f', '\x08']:
            """ backspace 退格键 """
            if self.retrieve:
                if not self.command:
                    self.control_string.append('\x07')
                else:
                    _retrieve_cmd = self.retrieve_cmd[:-1]
                    retrieve = retrieve_command(_retrieve_cmd, self.command_list)
                    if not retrieve:
                        self.control_string.append('\x07')
                        return
                    _command, self.retrieve_index, _command_cursor = retrieve
                    if self.retrieve_cmd:
                        # 先把命令清除
                        self.control_string.append('\x08' * (len(self.command) - self.command_cursor + 4) + '\x1b[K')
                        # 添加新增的字符
                        foo = "\': {0}{1}".format(_command, '\x08' * _command_cursor)
                        self.control_string.append(foo)
                    else:
                        self.control_string.append('\x07')
                    self.retrieve_cmd = _retrieve_cmd
                    self.command = _command
                    self.command_cursor = _command_cursor
                return
            if self.command:
                if not self.command_cursor:
                    self.command = self.command[0:-1]
                    self.control_string.append('\x08\x1b[K')
                elif len(self.command) == self.command_cursor:
                    self.control_string.append('\x07')
                else:
                    i = self.command[-self.command_cursor:]
                    self.control_string.append('\x08\x1b[1P{0}{1}'.format(i, '\x08' * len(i)))
                    self.command = self.command[:int(-self.command_cursor - 1)] + i
            else:
                self.control_string.append('\x07')

        elif data == '\x1b[3~':
            """ delete 键 """
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                self.control_string.append('\r' + self.user_ps1 + self.command)
                # 光标放回
                self.control_string.append('\x08' * self.command_cursor)
                self.tab = False
                self.retrieve = False
                self.retrieve_index = 0
                self.retrieve_cmd = ''
            if self.command:
                left = self.command[:-self.command_cursor] if self.command_cursor else self.command
                right = self.command[-self.command_cursor:] if self.command_cursor else ''
                if right:
                    self.control_string.append('\x07\x1b[1P\x07')
                    self.command = left + right[1:]
                    self.command_cursor -= 1
                else:
                    return
            else:
                self.control_string.append('\x07')
                self.logout = True

        elif data == '\x19':
            """ control + y 复制命令 """
            if self.retrieve:
                self.control_string.append('\x07')
                return
            if self.command_y:
                if self.command_cursor:
                    x = len(self.command) - self.command_cursor
                    temp_len = len(self.command)
                    self.command = self.command[:x] + self.command_y + self.command[x:]
                    self.control_string.append('\x1b[C' * self.command_cursor)  # cursor move to end
                    self.control_string.append('{0}\x1b[K'.format('\x08' * temp_len))  # clean line
                    self.control_string.append(self.command)    # output new command
                    self.control_string.append('\x08' * self.command_cursor)  # move cursor to old position
                else:
                    self.command += self.command_y
                    self.control_string.append(self.command_y)

        elif data == '\x15':
            """ control + U 控制符(清理当前命令行) """
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                self.control_string.append('\r' + self.user_ps1 + self.command)
                # 光标放回
                self.control_string.append('\x08' * self.command_cursor)
                self.tab = False
                self.retrieve = False
                self.retrieve_index = 0
                self.retrieve_cmd = ''
            if self.command_cursor:
                i = self.command[:-self.command_cursor]
                self.command_y = i
                n = self.command[-self.command_cursor:]
                self.control_string.append('{0}\x1b[{1}P{2}{3}'.format('\x08' * len(i), len(i), n, '\x08' * len(n)))
                self.command = n
            else:
                self.command_y = self.command
                self.control_string.append('{0}\x1b[K'.format('\x08' * len(self.command)))
                self.command = ''

        elif data == '\x0b':
            """ control + K 控制符(清理当前光标到行尾) """
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                self.control_string.append('\r' + self.user_ps1 + self.command)
                # 光标放回
                self.control_string.append('\x08' * self.command_cursor)
                self.tab = False
                self.retrieve = False
                self.retrieve_index = 0
                self.retrieve_cmd = ''
            if self.command_cursor:
                i = self.command[-self.command_cursor:]
                self.command_y = i
                n = self.command[:-self.command_cursor]
                self.control_string.append('\x1b[C' * self.command_cursor)  # cursor move to end
                self.control_string.append('{0}\x1b[K'.format('\x08' * len(i)))  # clean line
                self.command_cursor = 0
                self.command = n
            else:
                self.control_string.append('\x07')

        elif data == '\x17':
            """control + W 控制符(删除光标前一个字符串) """
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                self.control_string.append('\r' + self.user_ps1 + self.command)
                # 光标放回
                self.control_string.append('\x08' * self.command_cursor)
                self.tab = False
                self.retrieve = False
                self.retrieve_index = 0
                self.retrieve_cmd = ''
            left = self.command[:-self.command_cursor] if self.command_cursor else self.command
            right = self.command[-self.command_cursor:] if self.command_cursor else ''
            # '1 2 [光标位置]34' ---> '1 [光标位置]34'
            if left.endswith(' '):
                if not re.match('^\s*$', left):
                    space = re.match('(.*?)(\s+$)', left).group(2)
                    self.command_y = left.split()[-1] + space
                    mid_index = left.rfind(self.command_y)
                    to_append = left[:mid_index]
                else:
                    self.command_y = left
                    to_append = ''
            # '1 2 3[光标位置]4' ---> '1 2 [光标位置]4'
            elif left.strip().find(' '):
                mid_index = left.rfind(' ')
                self.command_y = left[mid_index+1:]
                to_append = left[:mid_index+1]
            # '123[光标位置]4' ---> '[光标位置]4'
            else:
                to_append = left[:-self.command_cursor]
                self.command_y = to_append
            self.control_string.append('{0}\x1b[{1}P{2}{3}'.format('\x08' * len(self.command_y),
                                                                   len(self.command_y), right, '\x08' * len(right)))
            self.command = to_append + right

        elif data == '\x0c':
            """ control + L 控制符(清理终端) """
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                self.control_string.append('\r' + self.user_ps1 + self.command)
                # 光标放回
                self.control_string.append('\x08' * self.command_cursor)
                self.tab = False
                self.retrieve = False
                self.retrieve_index = 0
                self.retrieve_cmd = ''
            if self.command_cursor:
                self.control_string.append(
                    '\x1b[H\x1b[2J{0}{1}{2}'.format(self.user_ps1, self.command, '\x08' * self.command_cursor)
                )
            else:
                self.control_string.append('\x1b[H\x1b[2J{0}{1}'.format(self.user_ps1, self.command))

        elif data in ['\x1b[D', '\x02']:
            """ <- 方向键, control + B """
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                self.control_string.append('\r' + self.user_ps1 + self.command)
                # 光标放回
                self.control_string.append('\x08' * self.command_cursor)
                self.tab = False
                self.retrieve = False
                self.retrieve_index = 0
                self.retrieve_cmd = ''
            if self.command_cursor == len(self.command):
                self.control_string.append('\x07')
            else:
                self.command_cursor += 1
                self.control_string.append('\x08')

        elif data in ['\x1b[C', '\x06']:
            """ -> 方向键, control + F"""
            if self.retrieve:
                # ctrl + r 模式下
                command_length = len(self.retrieve_ps1) + len(self.retrieve_cmd) + len(self.command)
                # 移到行尾
                self.control_string.append('\x1b[C' * self.command_cursor)
                # 移到行首
                self.control_string.append('\x08' * command_length)
                self.control_string.append('\x1b[K')
                # 重置回原生用户提示
                self.control_string.append('\r' + self.user_ps1 + self.command)
                # 光标放回
                self.control_string.append('\x08' * self.command_cursor)
                self.tab = False
                self.retrieve = False
                self.retrieve_index = 0
                self.retrieve_cmd = ''
            if self.command_cursor:
                self.command_cursor -= 1
                self.control_string.append('\x1b[C')
            else:
                self.control_string.append('\x07')

        elif data in ['\x1b[A', '\x10']:
            """ 向上 方向键, control + P """
            if self.retrieve:
                self.control_string.append('\x07')
                return
            if not self.command_list:
                self.control_string.append('\x07')
            elif self.command_index == 0:
                self.control_string.append('\x07')
            else:
                if self.command_cursor != 0:
                    self.control_string.append('{0}'.format('\x1b[C' * self.command_cursor))
                    self.command_cursor = 0
                self.command_index -= 1
                if not self.command:
                    self.control_string.append(self.command_list[self.command_index])
                elif len(self.command) < len(self.command_list[self.command_index]):
                    if self.command_list[self.command_index].startswith(self.command):
                        self.control_string.append(self.command_list[self.command_index][len(self.command):])
                    else:
                        self.control_string.append(
                            '{0}{1}'.format('\x08' * len(self.command), self.command_list[self.command_index])
                        )
                elif len(self.command) > len(self.command_list[self.command_index]):
                    self.control_string.append(
                        '{0}{1}\x1b[K'.format('\x08' * len(self.command), self.command_list[self.command_index])
                    )
                elif len(self.command) == len(self.command_list[self.command_index]):
                    self.control_string.append(
                        '{0}{1}'.format('\x08' * len(self.command), self.command_list[self.command_index])
                    )
                self.command = self.command_list[self.command_index]

        elif data in ['\x1b[B', '\x0e']:
            """ 向下 方向键, control + N """
            if self.retrieve:
                self.control_string.append('\x07')
                return
            if not self.command_list:
                self.control_string.append('\x07')
            elif self.command_index >= len(self.command_list):
                self.control_string.append('\x07')
            elif not self.command:
                self.control_string.append('\x07')
            else:
                if self.command_cursor:
                    self.control_string.append('{0}'.format('\x1b[C' * self.command_cursor))
                    self.command_cursor = 0
                self.command_index += 1
                if self.command_index == len(self.command_list):
                    self.control_string.append('{0}\x1b[K'.format('\x08' * len(self.command)))
                    self.command = ''
                elif len(self.command) > len('a'):
                    self.control_string.append(
                        '{0}{1}\x1b[K'.format('\x08' * len(self.command), self.command_list[self.command_index])
                    )
                    self.command = self.command_list[self.command_index]
                elif len(self.command) <= len(self.command_list[self.command_index]):
                    self.control_string.append(
                        '{0}{1}'.format('\x08' * len(self.command), self.command_list[self.command_index])
                    )
                    self.command = self.command_list[self.command_index]

        else:
            # 中文或者其它不支持的特殊控制字符
            self.command = ''
            self.tab = False
            self.command_cursor = 0
            self.command_index = len(self.command_list)
            self.enter = True
            msg = get_colour(u'\r\n您输入的字符里包含当前终端不支持的快捷键或中文字符  >_<||| \r\n')
            self.control_string.append(data)
            self.control_string.append(msg)

    def get_password(self, status, proxy_channel, message='Password: '):
        """ 处理终端输入密码 """
        password = ''
        temp = status[proxy_channel]
        status[proxy_channel] = 2
        proxy_channel.sendall(message)
        while True:
            p = self.password_receive.recv()
            # 避免删除提示符
            flag_password = password
            if p == '\x03':
                password = '^C'
                break
            elif p.find('\r') != -1:
                if p != '\r':
                    password = p[:-1]
                proxy_channel.sendall('\r\n')
                break
            elif p in ['\x7f', '\x08']:
                if len(password) == 1:
                    password = ''
                elif len(password) > 1:
                    password = password[:-1]
            elif p.encode("string-escape").startswith('\\'):
                if p.encode("string-escape") == "\\\'":
                    p = '\''
                elif p.encode("string-escape") == "\\\\":
                    p = '\\'
                else:
                    continue
            if p in ['\x7f', '\x08']:
                if len(flag_password):
                    proxy_channel.sendall('\x08\x1b[K')
            else:
                password += p
                proxy_channel.sendall('*' * len(p))
        status[proxy_channel] = temp
        return password

    def get_interruption(self, proxy_channel, jumper, popen=None):
        output = ''
        temp = jumper.status[proxy_channel]
        jumper.status[proxy_channel] = 2
        if popen == 'pssh':
            # pssh/plog 命令, 没按ctrl+c 中止
            while self.pause is False:
                getput = self.password_receive.recv()
                if getput == '\x03':
                    output = '^C'
                    self.pause = True
                    break
                elif getput == '\r':
                    proxy_channel.sendall('\r\n')
                elif not getput.encode("string-escape").startswith('\\'):
                    output = getput
                    proxy_channel.sendall(output)
                else:
                    pass
        else:
            # ping 命令, 没按ctrl+c 中止
            while self.pause is False:
                getput = self.password_receive.recv()
                if getput == '\x03':
                    output = '^C'
                    popen.terminate()
                    self.pause = True
                    pids = [pid for pid in command_pids.get('channel_{0}'.format(proxy_channel.get_id())) if pid != popen.pid]
                    command_pids['channel_{0}'.format(proxy_channel.get_id())] = pids
                    proxy_channel.sendall("^C\r")
                    break
                elif getput == '\r':
                    proxy_channel.sendall('\r\n')
                elif not getput.encode("string-escape").startswith('\\'):
                    output = getput
                    proxy_channel.sendall(output)
                else:
                    pass
        jumper.status[proxy_channel] = temp
        return output
