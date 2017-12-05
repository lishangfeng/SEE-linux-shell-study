#!/bin/env python
# -*- coding:utf-8 -*-

import json
import requests
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def date_handler(obj):
    if isinstance(obj, datetime):
        return str(obj)


def http_client(url, method='get', **kwargs):
    request_param = dict(
        headers=kwargs.get('headers', {}),
        cookies=kwargs.get('cookie', {}),
        timeout=kwargs.get('timeout', 30)
    )
    if method in ['post', 'put', 'delete']:
        if kwargs.get('json'):
            result = getattr(requests, method)(url, json=kwargs.get('json'), **request_param)
        elif kwargs.get('data'):
            data = json.dumps(kwargs.get('data'), default=date_handler)
            result = getattr(requests, method)(url, data=data, **request_param)
        else:
            result = getattr(requests, method)(url, **request_param)
    else:
        result = requests.get(url, **request_param)
    return result
