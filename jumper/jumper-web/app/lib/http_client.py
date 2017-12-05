#!/bin/env python
# -*- coding:utf-8 -*-

import requests


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
            result = getattr(requests, method)(url, data=kwargs.get('data'), **request_param)
        else:
            result = getattr(requests, method)(url, **request_param)
    else:
        result = requests.get(url, **request_param)
    return result
