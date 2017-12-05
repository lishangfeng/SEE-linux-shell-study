# -*- coding:utf-8 -*-

import logging
import re
import sys

from app.lib.async import Async
from app.lib.notice import Notice
from app.lib.thread_pool import ThreadPool
from app.lib.utils import check_unicode
from ansi_control import ANSI

from app.ssh_server.init import config


class CmdRecorder:
    """
    session_uuid    登录uuid
    login_uuid      会话uuid
    user_name	    用户名
    login_name      登录名
    host_name	    目标机器
    command		    命令
    exec_time	    执行时间
    danger	
    
    """
    def __init__(self, backend_server):
        self.user_name = config['user_name']
        self.host_name = backend_server.host_name
        self.login_name = backend_server.login_name
        self.login_uuid = backend_server.backend_uuid
        self.session_uuid = config['uuid']

        self.parser = ANSI()
        self.command = list()
        self.pool = ThreadPool(func=self.main, signal=True)
        logging.info(u'初始化命令记录: {0}'.format(self.session_uuid))

    def main(self, data):
        if data == sys.exit:
            self.done(truncation=False)
            return

        timestamp = data[1]
        cmd = self.parser.process(data[0])
        if cmd and check_unicode(cmd):
            danger = 0
            for rule in config['danger_regular']:
                if re.match(rule, cmd):
                    danger = 1
                    self.alert(cmd, timestamp)
                    break
            if danger:
                self.command.append([cmd, timestamp, danger])
            else:
                self.command.append([cmd, timestamp])

        if len(self.command) >= config['command_push_count']:
            self.done(truncation=True)

    def done(self, truncation=None):
        if len(self.command) == 0:
            return
        record_info = dict(
                user_name=self.user_name,
                login_name=self.login_name,
                host_name=self.host_name,
                login_uuid=self.login_uuid,
                session_uuid=self.session_uuid,
                command=self.command)
        if truncation:
            logging.info(u'分批上传历史命令: {0}'.format(self.session_uuid))
            self.command = []
        config['task'].add_task(Async.backend_command, data=record_info)

    def alert(self, cmd, timestamp):
        msg = u"""【Jumper发现危险命令】
    用户: {0}
    执行账号: {1}
    目标机器: {2}
    执行命令: {3}
    执行时间: {4}
    录像uuid: {5}
"""
        notice = msg.format(self.user_name, self.login_name, self.host_name, cmd, timestamp, self.login_uuid)
        Notice(notice, config['warning_user'])

    def wait_completion(self):
        self.pool.wait_completion()
