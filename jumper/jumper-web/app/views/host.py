# -*- coding: utf-8 -*-

from app.models import Auth
from app.models import Host
from app.models import Sudo
from app.lib.restful import *
from app.host.host_cache import HostCache
from app.lib.view_decorator import ViewDecorator


@ViewDecorator('/host', methods=['GET'])
def host_get(data):
    return RestfulGet(Host, data['get']).result


@ViewDecorator('/host/flush', methods=['GET'])
def host_flush(data):
    if data['get'].get('flush'):
        host_info = dict(host_ip=data['get']['host_ip'])
        HostCache(host_info).start()
    return HostCache.fetch_host(host_ip=data['get']['host_ip'])


@ViewDecorator('/host/<int:id>', methods=['PUT'])
def host_update(data):
    result = RestfulPut(Host, data['get']['id'], data['post']).result
    if result:
        HostCache(result).start()
    return result


@ViewDecorator('/host', methods=['POST'])
def host_add(data):
    result = RestfulPost(Host, data['post']).result
    if result:
        HostCache(result).start()
    return result


@ViewDecorator('/host/<int:id>', methods=['DELETE'])
def host_delete(data):
    host_info = data['host_info']
    Auth.query.filter_by(label='host_ip', label_key=host_info['host_ip']).delete()
    Auth.query.filter_by(label='host_name', label_key=host_info['host_name']).delete()
    Sudo.query.filter_by(label='host_ip', label_key=host_info['host_ip']).delete()
    Sudo.query.filter_by(label='host_name', label_key=host_info['host_name']).delete()

    temp = RestfulDelete(Host, data['get']['id']).result
    HostCache(host_info).start()
    return temp
