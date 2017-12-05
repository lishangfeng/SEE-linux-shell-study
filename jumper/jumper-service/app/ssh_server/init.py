# -*- coding:utf-8 -*-

import os
import socket
import paramiko
import linecache
from Queue import Queue

from lion import Lion

# 全局变量
config = dict()
Lion(interval=30, definitely=True).init_app(app_name='jumper-service', app_config=config)
commands_list = list()
command_pids = dict()
ssh_history = list()


class Init:
    """ 初始化系统 """
    def __init__(self, background=False):
        if not background:
            print self.get_colour(u'初始化系统...', colour='yellow')
        self.config = config
        self.app_env = 'product'
        self.config['background'] = background
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.init_config()
        self.load_ssh_key()
        if not background:  # 安全考虑不输出配置信息
            for key in sorted(self.config):
                print self.get_colour(u'  {0:30} =>  {1}'.format(key, self.config[key]), colour='green')

    def init_config(self):
        if not config['background']:
            print self.get_colour(u'加载配置...', colour='yellow')
        self.config['exiting'] = False
        self.config['ssh_server_keys'] = list()
        self.config['data_queue'] = Queue()
        self.config['output_queue'] = Queue(5000)
        self.config['server_name'] = socket.gethostname()

    def load_ssh_key(self):
        keys_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys')
        for file_name in os.listdir(keys_dir):
            if not file_name.endswith('.key'):
                continue
            try:
                file_path = os.path.join(keys_dir, file_name)
                line = linecache.getline(file_path, 1)
                if 'BEGIN RSA' in line:
                    self.config['ssh_server_keys'].append(paramiko.RSAKey(filename=file_path))
                elif 'BEGIN DSA' in line:
                    self.config['ssh_server_keys'].append(paramiko.DSSKey(filename=file_path))
            except Exception as e:
                print u'载入服务key: {0} 失败: {1}'.format(file_name, str(e))

    @staticmethod
    def get_colour(msg, colour='red'):
        try:
            if colour == 'red':
                return u'\033[31m{0}\033[0m'.format(msg)
            elif colour == 'green':
                return u'\033[32m{0}\033[0m'.format(msg)
            elif colour == 'yellow':
                return u'\033[33m{0}\033[0m'.format(msg)
            else:
                return msg
        except UnicodeDecodeError:
            return msg

if __name__ == '__main__':
    Init()
