#!/bin/env python
# -*- coding:utf-8 -*-

import datetime
from flask import current_app as app

from app.models import Auth
from app.models import Host
from app.models import Mapper
from app.lib.utlis import concat_tag


class AuthPermit:
    def __init__(self, request_data):
        self.uid = request_data['user_info']['uid']
        self.role = request_data['user_info']['role']
        self.enable = request_data['user_info']['enable']
        self.user_name = request_data['user_info']['login_name']
        self.host_ip = request_data['get']['host_ip']
        self.host_fqdn = request_data['get']['host_name']  # get host_fqdn from url params
        self.order_list = list()
        self.temp_list = list()

    def auth(self):
        """
        Auth Order - TEST_AUTH --> ADMIN_ROLE --> QA_ROLE(cluster in ['test', 'beta'])

        Auth Order - user:  host_ip --> host_fqdn --> cluster --> srv --> pdl --> owt
        Auth Order - group:  host_ip --> host_fqdn --> cluster --> srv --> pdl --> owt
        """
        if app.config.get('TEST_AUTH', None):
            app.logger.debug(u'开启了TEST_AUTH, 忽略权限校验用户登录权限.')
            return True
        elif self.role in app.config.get('ADMIN_ROLE', ['sa', 'op', 'sre']):
            app.logger.debug(u'用户{0}属于{1}角色, 跳过普通用户鉴权流程.'.format(self.user_name, self.role))
            return True

        self.order_list.append(dict(label='host_ip', label_key=self.host_ip))
        self.order_list.append(dict(label='host_fqdn', label_key=self.host_fqdn))
        # ip重复情况下，根据fqdn判断主机
        hosts = Host.query.filter_by(host_ip=self.host_ip).all()
        if len(hosts) == 1:
            host_info = hosts[0]
        else:
            host_info = Host.query.filter_by(host_fqdn=self.host_fqdn).first()
        if host_info:
            if host_info.owt == 'ep' and host_info.pdl not in ['metrics', 'sonar']:
                app.logger.debug(u'owt为ep的主机并且pdl不在metrics和sonar中, 允许所有人登陆, 用户{0}通过登录'.format(self.user_name))
                return True
            if self.role in app.config.get('QA_ROLE', ['qa']):
                if host_info.cluster in ['test', 'beta']:
                    if host_info.owt == 'ep' and host_info.pdl in ['metrics', 'sonar']:
                        # 拒绝用户角色为qa的人登陆ep下面pdl属于['metrics', 'sonar']下面的机器
                        pass
                    else:
                        app.logger.debug(u'用户{0}通过qa角色登陆cluster=(test,beta)成功'.format(self.user_name))
                        return True
            # 兼容主机名不是fqdn的情况
            if host_info.host_name == self.host_fqdn:
                self.order_list[1]['label_key'] = host_info.host_fqdn

            for tag in ['corp', 'owt', 'pdl', 'srv', 'cluster']:
                if getattr(host_info, tag):
                    label_key = concat_tag(host_info.to_dict(), tag)
                    if not label_key:
                        break
                    self.temp_list.append(dict(label=tag, label_key=label_key))
        self.order_list = self.order_list + self.temp_list[::-1]

        if self.role_user():
            app.logger.debug(u'用户{0}通过临时权限'.format(self.user_name))
            return True
        data = self.role_group()
        if data == -1:
            return False
        elif data is True:
            return True

    def role_user(self):
        for i in self.order_list:
            query = dict(role='user', role_id=self.uid, label=i['label'], label_key=i['label_key'])
            data = Auth.get_by(first=True, **query)
            if data:
                if data['life_cycle'] and data['life_cycle'] <= datetime.datetime.now():
                    Auth.delete(**data)
                    app.logger.info(u'用户{0}临时权限:{1},{2},life_cycle:{3}已过期, 清理记录.'.format(
                             self.user_name,
                             data['label'],
                             data['label_key'],
                             data['life_cycle']))
                    return False
                app.logger.info(u'用户{0}临时权限鉴权成功.'.format(self.user_name))
                return True

    def role_group(self):
        for i in self.order_list:
            query = dict(role='group', label=i['label'], label_key=i['label_key'])
            for data in Auth.get_by(**query):
                if data['life_cycle'] and data['life_cycle'] <= datetime.datetime.now():
                    Auth.delete(**data)
                    app.logger.info(u'用户{0}临时权限:{1},{2},life_cycle:{3}已过期, 清理记录.'.format(
                         self.user_name,
                         data['label'],
                         data['label_key'],
                         data['life_cycle']))
                    return False
                if Mapper.query.filter_by(uid=self.uid, gid=data['role_id']).first():
                    app.logger.info(u'用户{0}所在组{1}鉴权成功.'.format(self.user_name, i['label_key']))
                    return True

                if Auth.query.filter_by(label=i['label'], label_key=i['label_key']).first():
                    app.logger.info(u'用户{1}所在组{0}权限被继承覆盖, 用户没有该组权限.'.format(i['label_key'], self.user_name))
                    return -1