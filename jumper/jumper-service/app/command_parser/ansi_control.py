# -*- coding:utf-8 -*-

import re
import logging
import sys
sys.setrecursionlimit(2000)

"""
    shell下终端特殊字符意义, 简化版

    \x1b[{n}P   行中删除n个字符串
    \x1b[5@     unknow
    \r          回行首，顶格
    \x1b[K      删到光标位置
    \x08        <-- 向左移动
    \x1b[D      <-- 向左移动 不同终端兼容
    \x1b[C      --> 向右移动
    \x07        终端响铃
"""


class ANSI:
    def __init__(self):
        self.cmd = []
        self.command = ''
        self.cursor = 0
        self.ctl1 = re.compile('^\x1b\[\d+P')
        self.ctl2 = re.compile('^\x1b\[K')
        self.ctl3 = re.compile('^\x1b\[\d+@')

    def process(self, data):
        # print 'command0-->', data【0】.encode('string-escape')
        raw = self.pre_filter(data)
        if raw is None:
            return
        try:
            self.command_parse(raw)
            self.command_filter()
        except Exception as e:
            logging.error(u'解析命令出错:{0}'.format(raw.encode('string-escape')))
            logging.error(u'解析命令出错原因:{0}'.format(str(e)))

        self.cursor = 0
        self.cmd = []
        return self.command.strip()

    @staticmethod
    def pre_filter(raw_cmd):
        # 过滤异常长的命令避免递归超限
        # 为何和jumper.py那边重复，因为追加的命令不能保证是否大于1000个字符
        if len(raw_cmd) >= 1000:
            return None

        # 替换响铃
        raw_cmd = raw_cmd.replace('\x07', '')

        # 判断vim模式
        # '\x1b[m\x1b[4m1\x1b[m\x1b[15;99H2\x1b[12;6H\x1b[?12l\x'
        r1 = re.compile('\x1b\[\d+?;\d?')
        r2 = re.compile('\x1b\[\d+?;\d?H')
        r3 = re.compile('\x1b\[\d+?m')
        if re.findall(r1, raw_cmd) or re.findall(r2, raw_cmd) or re.findall(r3, raw_cmd):
            return None

        if not len(raw_cmd):
            return None
        return raw_cmd

    def command_parse(self, raw):
        if raw.startswith('\x1b[C'):
            """ --> """
            if self.cursor != 0:
                self.cursor += 1
            if len(raw) == len('\x1b[C'):
                return
            raw = raw[len('\x1b[C'):]
        elif raw.startswith('\x1b[D'):
            """ <-- """
            self.cursor -= 1
            if len(raw) == len('\x1b[D'):
                return
            raw = raw[len('\x1b[D'):]

        elif re.match(self.ctl1, raw):
            """ Mid Del """
            len1 = len(re.match(self.ctl1, raw).group())
            if len(self.cmd) == 0:
                pass
            elif self.cursor != 0:
                self.cmd = self.cmd[:self.cursor]
                self.cursor = 0
            if len(raw) == len1:
                return
            raw = raw[len1:]
        elif re.match(self.ctl2, raw):
            """ Last Del """
            len2 = len(re.match(self.ctl2, raw).group())
            if len(raw) == len2:
                return
            self.cmd = self.cmd[:self.cursor]
            self.cursor = 0
            raw = raw[len2:]
        elif re.match(self.ctl3, raw):
            """ \x1b[9@ unknow meaning """
            len3 = len(re.match(self.ctl3, raw).group())
            raw = raw[len3:]
        elif raw[0] == '\r':
            """ 顶格 """
            self.cursor = 0
            del self.cmd[:]
            if len(raw) == 1:
                return
            raw = raw[1:]
        elif raw[0] == '\x08':
            """ <-- """
            self.cursor -= 1
            if len(raw) == 1:
                return
            raw = raw[1:]
        elif raw[0] == '\x1b':
            """ ESC """
            if len(raw) == 1:
                return
            raw = raw[1:]
        else:
            """ Not ANSI Control String """
            if self.cursor != 0:
                self.cmd = self.cmd[:self.cursor]
                self.cursor = 0
            self.cmd.append(raw[0])
            if len(raw) == 1:
                return
            raw = raw[1:]
        self.command_parse(raw)

    def command_filter(self):
        # 过滤收尾不可见字符
        self.command = ''.join(self.cmd)
        self.command = self.command.strip()

        # 切割多余的PS1
        ps = re.match('^\[.+?@.+?\].', self.command)
        if ps:
            self.command = self.command[len(ps.group(0)):].strip()

    def wait(self):
        """ for testing """
        print self.cmd
        print ''.join(self.cmd)
        raw_input('....')


if __name__ == '__main__':
    """ 测试字符 """
    cmd = '\r\x1b[3P(reverse-i-search)`\':\x1b[C\x08\x08\x08c\': cd /data/manifests/\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x1b[1@d\x1b[C\x1b[C\x1b[C\x08\x08\x08\x1b[1@ \x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[9P1234567\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08'
    cmd = 'cd /data/manifests/\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08tail /var/log/secure\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x1b[9Pcd /dts/log\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08tail /var/log/secure\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x1b[1Pcd /data/manifests/\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08ls\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08cd\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08tail /var/log/secure\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x1b[10Pcd 1234567'
    cmd = 'cd /data/apl\x07j\x07\x07\x08\x1b[K\x08\x1b[Ko\x07\x08\x1b[Kl\x07o\x07\x08\x1b[K\x08\x1b[K\x08\x1b[K\x08\x1b[Kmai\x07n\x07\x08\x1b[K\x08\x1b[K\x08\x1b[Kanifests/'
    cmd = '123456\x08\x08\x08\x1b[C\x1b[C\x1b[C\x08\x08\x08\x08\x1b[1P456\x08\x08\x08\x1b[C\x1b[1P6\x08\x08\x08\x08tail /var/log/secure'
    cmd = 'cd /\r\x1b[1@(reverse-i-search)`\':\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C'
    cmd = 'cd /\r\x1b[1@(reverse-i-search)`\':\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C'
    cmd = '\r\x1b[5@(reverse-i-search)`\':\x1b[C\x08\x08\x08c\': cd 1234567\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x1b[1@d\x1b[C\x1b[C\x1b[C'
    cmd = '\r\x1b[9@(reverse-i-search)`\':\x1b[C\x08\x08\x08c\': cd /\x08\x08\x08\x08\x08\x08\x08\x1b[1@d\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[C\x1b[Cdata/manifests/\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08'
    cmd = 'cd \x07/data/manifests/'
    cmd = '\r(reverse-i-search)`\': \x08\x08\x08c\': cd /data/manifests/\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08d\': cd /data/manifests/\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08'
    cmd = ' \r\x1b[1@(reverse-i-search)`\':\x1b[C\x1b[D\x1b[D\x1b[Dl\': ls /data/\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[1@s\x1b[C\x1b[C\x1b[C'
    cmd = cmd.replace('\x07', '')
    ansi = ANSI()
    ansi.process(cmd)
    print ansi.cmd
    print ''.join(ansi.cmd)
