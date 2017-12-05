# -*- coding:utf-8 -*-

from datetime import datetime


def date_handler(obj):
    if isinstance(obj, datetime):
        return str(obj)
