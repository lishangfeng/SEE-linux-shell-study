#!/bin/env python
# -*- coding:utf-8 -*-

import sys
import logging
import traceback
from Queue import Queue
from threading import Thread

from app.lib.utils import get_traceback


class Worker(Thread):
    def __init__(self, tasks, func=None, signal=None, daemon=True):
        Thread.__init__(self)
        self.func = func
        self.tasks = tasks
        self.signal = signal
        self.daemon = daemon
        self.start()

    def run(self):
        while True:
            args, kwargs = self.tasks.get()
            if self.func:
                func = self.func
            else:
                func, args = args[0], args[1:]

            if sys.exit in args:
                if self.signal:
                    self.__exec(func, *args, **kwargs)
                self.tasks.task_done()
                return
            else:
                self.__exec(func, *args, **kwargs)
                self.tasks.task_done()

    @classmethod
    def __exec(cls, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logging.error(u'未知异常, 请排查 -> {0}'.format(get_traceback()))
            logging.error(u'未知异常, 请排查 -> {0}, {1}'.format(str(e), traceback.format_exc()))


class ThreadPool:
    def __init__(self, num_threads=1, worker=None, func=None, signal=None, daemon=True, *args, **kwargs):
        if worker:
            [worker(*args, **kwargs) for _ in range(num_threads)]
        else:
            self.tasks = Queue()
            [Worker(tasks=self.tasks, func=func, signal=signal, daemon=daemon) for _ in range(num_threads)]

    def add_task(self, *args, **kwargs):
        self.tasks.put((args, kwargs))

    def wait_completion(self):
        self.tasks.join()

    def get_task(self):
        return self.tasks.queue

    def get_task_num(self):
        return self.tasks.qsize()


class AsyncThread(Thread):
    def __init__(self, target, *args, **kwargs):
        Thread.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.target = target
        self.daemon = True
        self.start()

    def run(self):
        self.target(*self.args, **self.kwargs)
