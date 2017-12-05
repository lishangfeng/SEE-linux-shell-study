#!/bin/env python
# -*- coding:utf-8 -*-

import requests
from flask import current_app as app

from app.lib.error_define import SupportError


class CmdbUtils:
    def __init__(self, **kwargs):
        self.type = kwargs.get('type', 'bu')
        self.name = kwargs.get('name', 'bu')
        self.data = dict()
        self.data_all = dict()
        self.api = u'http://api.cmdb.dp/api/v0.1/bu?count=1000'
        self.api_list = dict(
            auth_ip={
                'desc': u'根据ip获取bu,app, product',
                'url': u'http://api.cmdb.dp/api/v0.1/projects/by_ips?ip={0}'
            },
            bu={
                'desc': u'获取整个UB列表',
                'url': u'http://api.cmdb.dp/api/v0.1/bu?count=1000'
            },
            products={
                'desc': u'获取指定BU的产品线列表',
                'url': u'http://api.cmdb.dp/api/v0.1/bu/{0}/products?count=1000'
            },
            projects={
                'desc': u'获取指定产品线的应用列表',
                'url': u'http://api.cmdb.dp/api/v0.1/products/{0}/projects?count=1000'
            },
            app_info={
                'desc': u'获取应用信息',
                'url': u'http://api.cmdb.dp/api/v0.1/projects/{0}?count=1000'
            },
            app_host_list={
                'desc': u'获取应用机器列表',
                'url': u'http://api.cmdb.dp/api/v0.1/projects/{0}/devices?count=1000'
            },
            host_info={
                'desc': u'根据主机名获取主机信息',
                'url': u'http://api.cmdb.dp/api/v0.1/ci/s?q=_type:(server;vserver;docker;tx-vserver;hulk),hostname:{0}'
            },
            ip_host_info={
                'desc': u'根据ip地址获取主机信息',
                'url': u'http://api.cmdb.dp/api/v0.1/ci/s?q=_type:(server;vserver;docker;tx-vserver;hulk),private_ip:{0}'
            },
            search={
                'desc': u'模糊搜索应用名称',
                'url': u'http://api.cmdb.dp/api/v0.1/ci/s?q=_type:project,project_name:{0}*'
            }
        )
        self.main()

    def main(self):
        if self.name == 'all' or self.type == 'all':
            self.get_api(type='bu')
            function_name = self.get_all
        else:
            self.get_api()
            function_name = self.request_api
        self.data = function_name()
        return self.data

    def get_api(self, **kwargs):
        self.type = kwargs.get('type') if kwargs.get('type', False) else self.type
        self.name = kwargs.get('name') if kwargs.get('name', False) else self.name
        if self.type not in self.api_list.keys():
            raise SupportError(u'Hi Cmdb目前还木有该技能')
        if self.type == 'bu':
            self.api = self.api_list['bu'].get('url')
        else:
            self.api = self.api_list[self.type].get('url').format(self.name)
        return self.api

    def request_api(self, api=None):
        try:
            self.api = api if api else self.api
            self.data = requests.get(self.api, timeout=3).json()
        except Exception, e:
            app.logger.warning(u'调用CMDB接口失败: {0}'.format(str(e)))
        return self.data

    def get_all(self):
        self.data_all = dict()

        self.get_api(type='bu')
        self.request_api()
        for bu_name in [bu['bu_name'] for bu in self.data.get('bu', dict())]:
            self.get_api(type='products', name=bu_name)
            self.request_api()
            self.data_all[bu_name] = dict()
            for product_name in [product['product_name'] for product in self.data.get('products')]:
                self.get_api(type='projects', name=product_name)
                self.request_api()
                self.data_all[bu_name][product_name] = [project['project_name'] for project in self.data['projects']]
        return self.data_all
