# -*- coding:utf-8 -*-

import re

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
        self.cursor = 0
        self.danger = False
        self.ctl1 = re.compile('^\x1b\[\d+P')
        self.ctl2 = re.compile('^\x1b\[K')
        self.ctl3 = re.compile('^\x1b\[\d+@')

    def process(self, raw):
        raw = raw.replace('\x07', '')   # 替换响铃
        self.analysis(raw)
        if self.is_danger():
            print 'Danger', ''.join(self.cmd)
            self.danger = True
        print '结果list-->', self.cmd
        print '结果-->', ''.join(self.cmd)
        return ''.join(self.cmd), self.danger

    def analysis(self, raw):
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
            print 'cmd->', self.cmd
            print 'cursor->', self.cursor
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
        self.analysis(raw)

    def is_danger(self):
        command = ''.join(self.cmd)
        if len(command.strip()) == 0:
            return False

        rules = [
            'rm\s+/\s+-rf',
            'rm\s+-rf\s+/',
            'history\s+-c'
        ]

        for rule in rules:
            ru = re.compile(rule)
            if re.match(ru, ''.join(self.cmd)):
                return True

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
