# -*- coding:utf-8 -*-

import time
import logging
from termcolor import colored

from app.lib.async import Async
from app.lib.http_client import http_client
from app.lib.thread_pool import AsyncThread


class PtyPlay:
    def __init__(self, jumper, channel, max_wait=3, speed=1):
        self.max_wait = max_wait
        self.channel = channel
        self.jumper = jumper
        self.speed = speed

        self.msg = None
        self.stop = False
        self.pause = False
        self.recorder = None
        self.forward = False
        self.backward = False
        self.play_uuid = None

    def main(self, command):
        if not self.jumper.proxy_server.recorder_list:
            Async.get_recorder(self.jumper.proxy_server)

        command = [i for i in command.split(' ') if i]
        if len(command) == 1:
            tag = 0
            for i in self.jumper.proxy_server.recorder_list:
                if len(i['host_name']) > tag:
                    tag = len(i['host_name'])
            else:
                tag += 4
            self.channel.sendall(colored(u'序号\t' + u'目标机器' + ' ' * (tag - len(u'目标机器')) + u'登录时间' + ' ' *  14 + u'登出时间' + ' ' * 12 + u'录像时长\r\n', color='cyan'))
            for n, i in enumerate(self.jumper.proxy_server.recorder_list):
                data = u'{0}\t{1}{2} ~ {3}\t{4}s\r\n'.format(
                    n,
                    i['host_name'] + ' ' * (tag - len(i['host_name'])),
                    i['start_time'][:19],
                    i['end_time'][:19],
                    float('%.1f' % i['duration'])
                )
                self.channel.sendall(colored(data, color='green'))
            self.channel.sendall(colored(u"""
play        查看播放列表\r
play 序号   播放录像\r
空格键      暂停\r
->          方向键快进5秒\r
<-          方向键后退5秒\r\n\n""", color='cyan'))
            self.channel.sendall(self.jumper.user_ps1)

        elif len(command[1].split('-')) == 5:
            recorder_info = Async.get_recorder_by_uuid(command[1])
            if not recorder_info:
                self.channel.sendall(colored(u'录像貌似不存在\r\n', color='red'))
                self.channel.sendall(self.jumper.user_ps1)
            elif not self.fetch_recorder(recorder_info[0].get('path')):
                self.channel.sendall(colored(self.msg + '\r\n', color='red'))
                self.channel.sendall(self.jumper.user_ps1)
            else:
                self.jumper.status[self.channel] = 4
                logging.info(u'开始播放录像 {0}'.format(self.play_uuid))
                AsyncThread(self.play)

        else:
            try:
                recorder_info = self.jumper.proxy_server.recorder_list[int(command[1])]
                if not recorder_info.get('path'):
                    self.channel.sendall(colored(u'录像貌似不存在\r\n', color='red'))
                    self.channel.sendall(self.jumper.user_ps1)
                elif not self.fetch_recorder(recorder_info.get('path')):
                    self.channel.sendall(colored(self.msg + '\r\n', color='red'))
                    self.channel.sendall(self.jumper.user_ps1)
                else:
                    self.jumper.status[self.channel] = 4
                    logging.info(u'开始播放录像 {0}'.format(self.play_uuid))
                    AsyncThread(self.play)
            except (ValueError, IndexError):
                self.channel.sendall(colored(u'请输入正确的序号\r\n', color='red'))
                self.channel.sendall(self.jumper.user_ps1)

    def play(self):
        index = 0
        text = None
        delay = None
        now = time.time()
        while self.recorder['stdout']:
            if self.stop:
                logging.info(u'停止播放 {0}'.format(self.play_uuid))
                return
            elif self.forward:
                logging.info(u'快进5秒 {0}'.format(self.play_uuid))
                text = None
                self.forward = False
                if self.pause:
                    self.pause = False
                    self.channel.sendall('\x08\x1b[K' * 13)
                s = 0.0
                _index = index
                for _delay, _ in self.recorder['stdout'][index:]:
                    s += _delay
                    if s >= 5:
                        if _index == index:
                            index = _index + 1 if _index < len(self.recorder['stdout']) - 1 else _index
                        else:
                            index = _index
                        break
                    else:
                        _index += 1
                else:
                    index = len(self.recorder['stdout']) - 1
            elif self.backward:
                logging.info(u'后退5秒 {0}'.format(self.play_uuid))
                text = None
                self.backward = False
                if self.pause:
                    self.pause = False
                    self.channel.sendall('\x08\x1b[K' * 13)
                s = 0.0
                _index = index
                for _delay, _ in self.recorder['stdout'][index-1::-1]:
                    s += _delay
                    if s >= 5:
                        if _index == index:
                            index = _index - 1 if _index > 0 else _index
                        else:
                            index = _index
                        break
                    else:
                        _index -= 1
                else:
                    index = 0
            elif self.pause:
                time.sleep(0.001)
                continue

            if text is None:
                delay, text = self.recorder['stdout'][index]
                if self.max_wait and delay > self.max_wait:
                    delay = self.max_wait

            if time.time() - now >= delay:
                self.channel.sendall(text)
                text = None
                now = time.time()
                if index >= len(self.recorder['stdout']) - 1:
                    break
                else:
                    index += 1
            time.sleep(0.0001)

        logging.info(u'播放完毕 {0}'.format(self.play_uuid))
        self.channel.sendall('\r\n')
        self.channel.sendall(self.jumper.user_ps1)
        self.jumper.status[self.channel] = 0

    def fetch_recorder(self, path):
        try:
            self.recorder = http_client(path).json()
            self.play_uuid = self.recorder['login_uuid']
            logging.info(u'获取录像数据 {0}'.format(self.play_uuid))
            return self.recorder
        except ValueError:
            self.msg = u'录像数据格式错误'
        except Exception as e:
            self.msg = u'获取录像数据失败 {0}'.format(str(e))
        logging.error(self.msg)
