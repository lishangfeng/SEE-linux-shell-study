# -*- coding:utf-8 -*-

import time
import codecs
from datetime import datetime


class Output:
    def __init__(self, max_wait=10):
        self.start_time = datetime.now()
        self.end_time = datetime.now()
        self.size = 0
        self.frames = []
        self.max_wait = max_wait
        self.last_write_time = time.time()
        self.duration = 0
        self.decoder = codecs.getincrementaldecoder('UTF-8')('replace')

    def close(self):
        self.end_time = datetime.now()

    def write(self, data):
        # logging.debug(u'录像数据: {0}'.format(data.encode("string-escape")))
        text = self.decoder.decode(data)
        if text:
            delay = self._increment_elapsed_time()
            self.frames.append([delay, text])
            self.size = len(str(self.frames))
        return len(data)

    def _increment_elapsed_time(self):
        now = time.time()
        delay = now - self.last_write_time

        if self.max_wait and delay > self.max_wait:
            delay = self.max_wait

        self.duration += delay
        self.last_write_time = now

        return delay
