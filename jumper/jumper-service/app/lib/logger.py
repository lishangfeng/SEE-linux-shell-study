#!/bin/env python
# -*- coding:utf-8 -*-

import logging
import socket

from cloghandler import ConcurrentRotatingFileHandler

from app.ssh_server.init import config


class CustomFormatter(logging.Formatter):
    """ 自定义日志格式
    """
    def __init__(self, fmt):
        logging.Formatter.__init__(self, fmt=fmt)

    def format(self, record):
        if config.get('server_type') == 'process':
            setattr(record, 'uuid', '{0}:{1}'.format(config.get('uuid', None), config.get('user_name')))
        else:
            setattr(record, 'uuid', 'uuid')
        setattr(record, 'hostname', socket.gethostname())

        return logging.Formatter.format(self, record)


def init_logger():
    """ 初始化日志 """
    log_format = [
        '%(asctime)s',
        '%(hostname)s',
        '%(levelname)s',
        'pid:%(process)d',
        '%(uuid)s',
        '%(filename)s:%(lineno)d',
        '%(message)s'
    ]

    if config.get('background'):
        # 多进程下日志切割出现问题, 替换成多进程日志模块
        handler = ConcurrentRotatingFileHandler(filename=config['log_file'],
                                                maxBytes=config['log_size'],
                                                backupCount=config['log_rotate_backup_count'])
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter(fmt='\t'.join(log_format)))

    logger = logging.getLogger()
    logger.addHandler(handler)
    if config.get('log_level') in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
        logger.setLevel(getattr(logging, config['log_level']))
    else:
        logger.setLevel(logging.INFO)
