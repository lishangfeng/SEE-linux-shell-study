# -*- coding:utf-8 -*-

import logging
from functools import wraps


class ExitError(Exception):
    pass


def exception_wrapper(method):
    @wraps(method)
    def wrapped(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except ExitError:
            logging.info(u'  用户ctrl+c取消登录')
            return False
    return wrapped
