#!/bin/env python
# -*- coding:utf-8 -*-

import socket
import logging
from flask import request, g
from cloghandler import ConcurrentRotatingFileHandler


def get_client_ip():
    xff = request.headers.get('X-Forwarded-For')
    if xff:
        return xff.split(',')[0]
    else:
        return request.headers.get('X-Real-IP') or request.remote_addr


class CustomFormatter(logging.Formatter):
    def format(self, record):
        try:
            setattr(record, 'url', request.path)
        except RuntimeError:
            setattr(record, 'url', 'Null')
        try:
            setattr(record, 'uuid', g.uuid)
        except (RuntimeError, AttributeError):
            setattr(record, 'uuid', 'Null')
        try:
            setattr(record, 'remote_addr', get_client_ip())
        except RuntimeError:
            setattr(record, 'remote_addr', 'Null')
        setattr(record, 'hostname', socket.gethostname())
        return logging.Formatter.format(self, record)


class AppLogger:
    def __init__(self, app):
        self.app = app
        self.log_format = None
        self.handlers = []

        self.set_format()
        self.set_handler()
        self.get_logging()

    def set_format(self):
        log_format = [
            '%(asctime)s',
            '%(levelname)s',
            '%(uuid)s',
            '%(process)s',
            '%(remote_addr)s',
            '[URL:%(url)s]',
            '[%(filename)s:%(lineno)d]',
            '%(message)s'
        ]
        self.log_format = CustomFormatter('  '.join(log_format))

    def set_handler(self):
        # 多进程下日志切割出现问题, 替换成多进程模块
        handler_file = ConcurrentRotatingFileHandler(
            filename=self.app.config.get('APP_LOG'),
            maxBytes=self.app.config.get('LOG_SIZE'),
            backupCount=self.app.config.get('LOG_ROTATE_BACKUP_COUNT')
        )
        handler_file.setFormatter(self.log_format)
        self.handlers.append(handler_file)

    def get_logging(self):
        [self.app.logger.addHandler(handler) for handler in self.handlers]
        if self.app.config.get('LOG_LEVEL') in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            self.app.logger.setLevel(getattr(logging, self.app.config.get('LOG_LEVEL')))
        else:
            self.app.logger.setLevel(logging.DEBUG)
