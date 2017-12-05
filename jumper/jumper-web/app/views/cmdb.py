#!/bin/env python
# -*- coding:utf-8 -*-
from app.models import Host
from app.lib.cmdb import CmdbUtils
from app.lib.view_decorator import ViewDecorator


@ViewDecorator('/cmdb', methods=['GET'])
def cmdb(data):
    """
    cmdb接口,
    两个参数name, type
    """
    data = CmdbUtils(**data['get']).data
    if data.get('name') == 'bu' or not data:
        data = [name['bu_name'] for name in data['bu']]
    elif data.get('type') == 'products':
        data = [name['product_name'] for name in data['products']]
    elif data.get('type') == 'projects':
        data = [name['project_name'] for name in data['projects']]
    elif data.get('type') == 'app_host_list':
        data = data['devices']
    elif data.get('type') == 'app_info':
        data = data['project']
    elif data.get('type') == 'host_info':
        data = data['result'][0]
    elif data.get('type') == 'search':
        data = [name['project_name'] for name in data['result']]
    if isinstance(data, list):
        data.sort()
    return data


@ViewDecorator('/cmdb', methods=['POST'])
def ssh_cmdb(data):
    project = data['post']['project']
    try:
        # 避免用户输入数字传过来导致错误提示
        app_type = str(project).split('.')
    except:
        return []
    if len(app_type) == 1:
        query = dict(type='app_host_list', name=project)
        result = CmdbUtils(**query).data.get('devices', None)
        return [i['hostname'] + ':' + i['private_ip'][0] for i in result if i['env'] == u'生产'] if result else None
    elif len(app_type) == 3:
        owt, pdl, srv = app_type[0], app_type[1], app_type[2]
        data = Host.query.filter_by(owt=owt, pdl=pdl, srv=srv).all()
        return [i.host_name + ':' + i.host_ip for i in data]
    elif len(app_type) == 4:
        owt, pdl, srv, cluster = app_type[0], app_type[1], app_type[2], app_type[3]
        data = Host.query.filter_by(owt=owt, pdl=pdl, srv=srv, cluster=cluster).all()
        return [i.host_name + ':' + i.host_ip for i in data]
