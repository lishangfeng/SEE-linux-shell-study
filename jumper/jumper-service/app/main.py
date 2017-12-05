# -*- coding:utf-8 -*-

import logging
import os
import signal
import socket
import time
import traceback
from uuid import uuid4

from lion import Lion

from app.ssh_server.get_proxy import GetProxy
from app.ssh_server.init import Init
from app.ssh_server.init import config
from app.ssh_server.jumper import JumpServer
from app.ssh_server.tcp_server import Server
from lib.logger import init_logger
from lib.thread_pool import ThreadPool
from lib.utils import get_colour, get_traceback


class Main:
    def __init__(self, background=None):
        self.init = Init(background)
        self.pid = os.getpid()
        self.jumper = None

    def process(self):
        pid = os.fork()
        if not pid:
            Lion(interval=30, definitely=True).init_app(app_name='jumper-service', app_config=config)
            self.start_server()
        elif config.get('background'):
            return
        while True:
            try:
                pid, _ = os.wait()
            except OSError:
                return False
            except KeyboardInterrupt:
                time.sleep(0.5)
                return True
            print get_colour('Kill {0}'.format(pid))

    def start_server(self):
        print get_colour(u'启动主进程: {0}'.format(os.getpid()))
        signal.signal(signal.SIGTERM, self.after)
        signal.signal(signal.SIGINT, self.after)
        with open(config['pid_file'], 'w') as f:
            f.write('{0}\n'.format(os.getpid()))
        try:
            Server((config['ssh_server_ip'], int(config['ssh_server_port'])), self.handle).serve_forever()
        except socket.error as e:
            print get_colour(str(e))

    def handle(self, client_socket, client_address):
        if client_address[0] in config['health_check']:
            client_socket.close()
        else:
            try:
                init_logger()
                config['uuid'] = str(uuid4())
                config['task'] = ThreadPool()
                client = dict(client_socket=client_socket, client_ip=client_address[0], client_port=client_address[1])
                proxy_server = GetProxy(client).process()
                if proxy_server:
                    self.jumper = JumpServer()
                    self.jumper.proxy(proxy_server)
                    self.jumper.main()
                config['task'].wait_completion()
                logging.info(u'退出进程: pid:{0}'.format(os.getpid()))
            except Exception as e:
                logging.error(u'未知异常, 请排查 -> {0}'.format(get_traceback()))
                logging.error(u'未知异常, 请排查 -> {0}, {1}'.format(str(e), traceback.format_exc()))
                self.after()

    def after(self, *args):
        logging.info(u'收到退出信号: {0}, 退出进程'.format(str(args)))
        if self.jumper:
            self.jumper.close()
        if config.get('task'):
            config['task'].wait_completion()
        os._exit(0)
