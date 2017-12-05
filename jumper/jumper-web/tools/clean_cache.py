#!/bin/env python
# -*- coding:utf-8 -*-

import sys
import json
import urllib
import urllib2
from os import listdir, remove
from os.path import join


reload(sys)
sys.setdefaultencoding('utf-8')


def http_client(url, method='get', **kwargs):
    headers = kwargs.get('headers', dict())
    headers.update({'User-Agent': 'Crontab Job Clean Cache /dev/shm'})
    if method == 'post':
        if kwargs.get('data'):
            headers.update({'Content-Type': 'content-type: application/json'})
            data = json.dumps(kwargs.get('data'))
        else:
            data = urllib.urlencode(kwargs.get('values', dict()))
        request = urllib2.Request(url, headers=headers, data=data)
    else:
        request = urllib2.Request(url, headers=headers)
    try:
        return urllib2.urlopen(request, timeout=int(kwargs.get('timeout', 3))).read().strip()
    except Exception as e:
        print str(e)


if __name__ == '__main__':
    result = http_client("http://127.0.0.1:8080/api/nss/cache/version")
    version = []
    local_version = []

    try:
        data = json.loads(result)
        for uuid in data['result']:
            version.append(uuid['version'])

        for file in listdir("/dev/shm"):
            if len(file) == 36:
                local_version.append(file)

        for uuid in local_version:
            if uuid not in version:
                remove(join("/dev/shm", uuid))
    except Exception as e:
        print str(e)
