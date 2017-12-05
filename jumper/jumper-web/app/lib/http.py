# -*- coding: utf-8 -*-

import json
import requests
from datetime import datetime
from requests.exceptions import ConnectionError

session = requests.Session()


def date_handler(obj):
    if isinstance(obj, datetime):
        return str(obj)


def http(url, method='get', **kwargs):
    request_param = dict(
        headers=kwargs.get('headers', {}),
        cookies=kwargs.get('cookie', {}),
        timeout=kwargs.get('timeout', 30)
    )
    try:
        if method in ['post', 'put', 'delete']:
            if kwargs.get('json'):
                result = getattr(session, method)(url, json=kwargs.get('json'), **request_param)
            elif kwargs.get('data'):
                result = getattr(session, method)(url, data=kwargs.get('data'), **request_param)
            else:
                result = getattr(session, method)(url, **request_param)
        else:
            result = session.get(url, **request_param)
        return result
    except ConnectionError:
        pass


def http_json(url, method='get', **kwargs):
    request_param = dict(
        headers=kwargs.get('headers', {}),
        cookies=kwargs.get('cookie', {}),
        timeout=kwargs.get('timeout', 30)
    )
    try:
        if method in ['post', 'put', 'delete']:
            if kwargs.get('json'):
                result = getattr(session, method)(url, json=kwargs.get('json'), **request_param)
            elif kwargs.get('data'):
                result = getattr(session, method)(url, data=kwargs.get('data'), **request_param)
            else:
                result = getattr(session, method)(url, **request_param)
        else:
            result = session.get(url, **request_param)

        return result.json()
    except (ConnectionError, ValueError):
        return None


def beauty_json(data):
    # print json.dumps(data, indent=4, default=date_handler)
    return json.dumps(data, indent=4, default=date_handler)
