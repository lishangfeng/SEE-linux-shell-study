#!/bin/env python
# -*- coding:utf-8 -*-

import time
import json
from datetime import datetime

from app.lib.app_redis import Rds


def date_handler(obj):
    if isinstance(obj, datetime):
        return str(obj)


def json_loads(data):
    if isinstance(data, list):
        return [json_loads(i) for i in data]
    elif isinstance(data, tuple):
        return [json_loads(i) for i in data]
    elif isinstance(data, dict):
        return dict({k: json_loads(data[k]) for k in data.keys()})
    else:
        try:
            obj = json.loads(data)
            if obj == data:
                return data
            elif isinstance(obj, int) or isinstance(obj, str):
                return obj
            else:
                return json_loads(obj)
        except (TypeError, ValueError):
            return data


def get_session(user_name=None):
    """ 查询北京上海两地用户会话信息"""

    result = dict()
    mt_session = Rds.router().get_session()
    for user in mt_session:
        if not result.get(user.get('login_name')):
            result[user.get('login_name')] = dict()
            result[user['login_name']]['session'] = list()
            result[user['login_name']]['session_detail'] = list()
        ttl = time.strftime('%H:%M:%S', time.gmtime(int(user['ttl'])))
        result[user['login_name']]['session'].append('{0} expired after {1} hours'.format(user['uuid'], ttl))
        result[user['login_name']]['session_detail'].append(user)

    dp_session = Rds.router(source='dp').get_session()
    for user in dp_session:
        if not result.get(user.get('login_name')):
            result[user.get('login_name')] = dict()
            result[user['login_name']]['session'] = list()
            result[user['login_name']]['session_detail'] = list()
        ttl = time.strftime('%H:%M:%S', time.gmtime(int(user['ttl'])))
        result[user['login_name']]['session'].append('{0} expired after {1} hours'.format(user['uuid'], ttl))

    if user_name:
        if result.get(user_name, None):
            result[user_name].update(dict(session_count=len(result[user_name]['session'])))
            return result[user_name]
        return
    unique_session_count = 0
    for user in result:
        unique_session_count += len(result[user]['session'])
    return dict(unique_user_count=len(result), unique_session_count=unique_session_count, session_detail=result)


def concat_tag(host, tag):
    """owt-->pdl-->srv-->cluster"""
    enum = ['corp', 'owt', 'pdl', 'srv', 'cluster']
    concat_str = []
    for i in enum:
        if host.get(i):
            concat_str.append(host.get(i))
        else:
            return None
        if tag == i and host.get(i):
            return ".".join(concat_str)
        elif not host.get(i):
            return None
