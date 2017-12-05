#!/bin/env python
# -*- coding:utf-8 -*-

import json
from flask import Flask
from datetime import datetime


def date_handler(obj):
    if isinstance(obj, datetime):
        return str(obj)


def res(result=list(), code=200, msg='', response_class=True):
    """
    code 状态说明
    200: 正常处理
    203: 提交数据格式不对
    204: 提交数据非法
    205: 没有权限
    """
    if code == 200 and not msg:
        msg = u'操作完成'
    elif code == 203 and not msg:
        msg = u'提交的数据格式错误'
    elif code == 204 and not msg:
        msg = u'提交的数据非法'
    elif code == 205 and not msg:
        msg = u'Hi 您没有权限'
    result = dict(code=code, msg=msg, result=result)
    if response_class:
        return Flask.response_class(json.dumps(result, default=date_handler), mimetype='application/json')
    else:
        return json.dumps(result)


class ValidationError(Exception):
    def __init__(self, msg):
        self.msg = 'validation error: %s ' % msg
        Exception.__init__(self, self.msg)


class SupportError(Exception):
    def __init__(self, msg):
        self.msg = 'Not Support: %s' % msg
        Exception.__init__(self, self.msg)


class PermissionError(Exception):
    def __init__(self, msg=''):
        self.msg = msg
        Exception.__init__(self, self.msg)


class RedisError(Exception):
    def __init__(self, msg=''):
        self.msg = msg
        Exception.__init__(self, self.msg)


class RedisExceptionError(Exception):
    def __init__(self, msg=''):
        self.msg = msg
        Exception.__init__(self, self.msg)


class SQLAlchemyError(Exception):
    def __init__(self, msg=''):
        self.msg = msg
        Exception.__init__(self, self.msg)
