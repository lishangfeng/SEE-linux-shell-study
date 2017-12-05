# -*- coding:utf-8 -*-

import logging
import os
import sys
from datetime import datetime

from app.lib.async import Async
from app.lib.thread_pool import ThreadPool
from output import Output
from transport import Transport

from app.ssh_server.init import config


class PtyRecorder:
    def __init__(self, backend_server):
        self.user_name = backend_server.user_name
        self.host_name = backend_server.host_name
        self.term = backend_server.terminal['term']
        self.width = backend_server.terminal['width']
        self.height = backend_server.terminal['height']
        self.backend_uuid = backend_server.backend_uuid

        self.success = False
        self.output = Output()
        self.recorder_list = list()
        self.pool = ThreadPool(func=self.main, signal=True)
        logging.info(u'初始化录像: {0}'.format(self.backend_uuid))

    def main(self, data):
        if len(self.recorder_list) - 1 >= config.get('recorder_number', 20):
            return
        if data == sys.exit:
            self.done(truncation=False)
            return

        self.output.write(data)
        if self.output.size >= 5242880:
            self.done(truncation=True)

    def done(self, truncation=None):
        self.output.close()
        recorder_data = self.recorder_data()
        remote_path = os.path.join(self.user_name, str(datetime.now().strftime("%m")), recorder_data['title']) + '.json'
        recorder_info = dict(
            start_time=self.output.start_time,
            end_time=self.output.end_time,
            serial=len(self.recorder_list),
            size=self.output.size,
            duration=self.output.duration,
            title=recorder_data['title'],
            width=recorder_data['width'],
            height=recorder_data['height'],
            term=recorder_data['env']['term'],
            key=remote_path,
            path=Transport().upload(remote_path, self.output.size, recorder_data)
        )
        self.recorder_list.append(recorder_info)
        config['task'].add_task(Async.update_login, login_uuid=self.backend_uuid, recorder=self.recorder_list)
        if truncation:
            logging.info(u'切割录像文件: {0}'.format(recorder_info['serial']))
            self.output = Output()
        else:
            self.success = True
        if len(self.recorder_list) >= config.get('recorder_number', 20):
            logging.info(u'当前会话录像份数超限, 不再录像.')

    def recorder_data(self):
        title = u'{0}_{1}_{2}_{3}'.format(
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            self.host_name,
            self.backend_uuid.split('-')[-1],
            len(self.recorder_list)
        )
        return dict(
            version=1,
            start_time=self.output.start_time,
            end_time=self.output.end_time,
            width=self.width,
            height=self.height,
            login_uuid=self.backend_uuid,
            duration=self.output.duration,
            command=None,
            env=dict(
                term=self.term,
                SHELL='/bin/bash'
            ),
            stdout=self.output.frames,
            title=title
        )

    def wait_completion(self):
        self.pool.wait_completion()
