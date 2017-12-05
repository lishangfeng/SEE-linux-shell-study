# -*- coding:utf-8 -*-

import copy
import json
import logging
import os
from urlparse import urljoin

from app.lib.date_handler import date_handler
from app.lib.http_client import http_client

from app.ssh_server.init import commands_list
from app.ssh_server.init import config
from app.ssh_server.init import ssh_history


class Async:
    api_dict = dict(
        lock_user=dict(
            desc=u'用户登录失败, 更新失败次数',
            url=u'/api/jumper/locked'
        ),
        user_update=dict(
            desc=u'用户信息更新接口',
            url=u'/api/jumper/user'
        ),
        user_search=dict(
            desc=u'用户信息查询接口',
            url=u'/api/jumper/user'
        ),
        uuid=dict(
            desc=u'uuid接口',
            url=u'/api/jumper/uuid'
        ),
        login_history=dict(
            desc=u'登录历史接口',
            url=u'/api/jumper/login_history'
        ),
        clean_up=dict(
            desc=u'断开连接, 清理会话',
            url=u'/api/jumper/clean'
        ),
        command_history=dict(
            desc=u'伪终端历史命令接口',
            url=u'/api/jumper/history'
        ),
        backend_command=dict(
                desc=u'用户后端机器历史命令接口',
                url=u'/api/jumper/command'
        ),
        heartbeat=dict(
            desc=u'heartbeat心跳数据',
            url=u'/api/jumper/heartbeat'
        ),
        permission=dict(
            desc=u'不知道',
            url=u'/api/jumper/permission'
        ),
        cmdb=dict(
            desc=u'cmdb',
            url=u'/api/cmdb'
        ),
        cmdb_mt=dict(
            desc=u'cmdb_mt',
            url=u'/api/jumper/mt_cmdb'
        ),
        redis_password=dict(
            desc=u'redis_password',
            url=u'/api/web/redis_password'
        ),
        host_search=dict(
            desc=u'主机搜索接口',
            url=u'/api/host?host_name={0}'
        ),
        get_recorder=dict(
            desc=u'查询录像信息',
            url=u'/api/login?order_by=id&page_size=20&@logout_time=-&user_uid={user_uid}'
        ),
        get_recorder_by_uuid=dict(
            desc=u'查询指定uuid录像信息',
            url=u'/api/login?login_uuid={login_uuid}'
        )
    )

    def __init__(self):
        pass

    @classmethod
    def get_headers(cls, header=None):
        if header == 'token':
            return {'Authorization': config.get('api_token'), 'User-Agent': 'Jumper-Service'}
        return {'Authorization': config.get('takecare_token'), 'User-Agent': 'Jumper-Service'}

    @classmethod
    def takecare(cls, url, method, desc, **kwargs):
        try:
            _data = dict(url=url, method=method, data=kwargs)
            http_client(config.get('takecare'),
                        method='post',
                        headers=cls.get_headers(),
                        data=json.dumps(_data, ensure_ascii=False, default=date_handler))
            logging.info(u'接口错误兜底成功: {0}'.format(desc))
        except Exception as err:
            logging.error(u'接口错误兜底接口失败: {0}, {1}'.format(desc, str(err)))

    @classmethod
    def get_api(cls, name):
        api = cls.api_dict.get(name)
        api['url'] = urljoin(config.get('api_domain'), api['url'])
        return api

    @classmethod
    def request(cls, url, method='post', desc='', takecare=False, **kwargs):
        try:
            kwargs['headers'] = cls.get_headers(header='token')
            result = http_client(url=url, method=method, **kwargs)
            if result.status_code != 200:
                logging.error(u'Async 请求管理端失败: {0}, {1}, {2}'.format(desc, url, result.status_code))
                if takecare:
                    cls.takecare(url, method, desc, **kwargs)
                return
            else:
                data = result.json()

            if data['code'] != 200:
                logging.warning(u'Async 请求被拒绝: {0}, {1}, {2}'.format(desc, url, json.dumps(data, ensure_ascii=False)))
            else:
                logging.info(u'Async {0}'.format(desc))
                return data['result']
        except Exception as e:
            if takecare:
                cls.takecare(url, method, desc, **kwargs)
            logging.error(u'Async 访问失败: {0}, {1}, {2}'.format(desc, url, str(e)))

    @classmethod
    def convert_sha512(cls, uid, password):
        """ 更新用户密码加密方式 """
        cls.request(
            url=cls.get_api('user_update')['url'],
            method='put',
            desc=u'升级密码加密方式, uid: {0}'.format(uid),
            data=dict(query_string=dict(uid=uid), data=dict(password=password)),
            takecare=True
        )

    @classmethod
    def heartbeat(cls, proxy_server):
        """ 心跳信息 """
        data = dict(user_name=proxy_server.user_name, uuid=config['uuid'], data=list())
        for channel in proxy_server.channel_list:
            backend_record = "{0}:{1}:{2}".format(config['server_name'], channel.get_id(), os.getpid())
            if channel in proxy_server.backend_server:
                data['data'].append(backend_record + "&" + proxy_server.backend_server[channel].host_name)
            else:
                data['data'].append(backend_record + "&None")
        cls.request(
            url=cls.get_api('heartbeat')['url'],
            desc=u'更新heartbeat心跳数据',
            data=data,
            takecare=True
        )

    @classmethod
    def clean_up(cls, source):
        """ 退出Jumper, 清理session, 清理heartbeat """
        cls.request(
            url=cls.get_api('clean_up')['url'],
            desc=u'{0} 退出终端, 清理会话'.format(config['user_name']),
            data=dict(source=source, uuid=config['uuid'], username=config['user_name']),
            takecare=True
        )

    @classmethod
    def get_user(cls, query_dict):
        """ 查询用户信息 """
        query = []
        for k, v in query_dict.items():
            query.append('{0}={1}'.format(k, v))
        else:
            url = u'{0}{1}'.format(cls.get_api('user_search')['url'], '?' + '&'.join(query))
        return cls.request(
                   url=url,
                   method='get',
                   desc=u'查询用户信息 ' + str(query)
        )

    @classmethod
    def update_user(cls, uid, login_time):
        """ 更新用户信息登录时间 """
        data = dict(query_string=dict(uid=uid), data=dict(login_time=login_time))
        return cls.request(
                cls.get_api('user_update')['url'],
                method='post',
                desc=u'更新用户信息登录时间',
                data=data,
                takecare=True
        )

    @classmethod
    def update_password(cls, query_dict, data):
        """ 更新用户密码 """
        data = dict(query_string=query_dict, data=data)
        return cls.request(
                   cls.get_api('user_update')['url'],
                   method='put',
                   desc=u'更新用户密码',
                   data=data
        )

    @classmethod
    def lock_user(cls, login_name, failures):
        """ 记录密码错误次数, 用于临时锁定用户 """
        cls.request(
            url=cls.get_api('lock_user')['url'],
            method='post',
            desc=u'{0} 用户30分钟内, 登录失败 {1} 次'.format(login_name, failures),
            data=dict(lock_user_ttl=config['lock_user_ttl'] or 1800, login_name=login_name)
        )

    @classmethod
    def put_login(cls, login_info):
        """ 记录登录信息 """
        cls.request(
            url=cls.get_api('login_history')['url'],
            desc=u'记录登录历史 {0} --> {1}'.format(login_info['login_name'], login_info['host_name']),
            data=login_info,
            takecare=True
        )

    @classmethod
    def get_login(cls, uid):
        """ 获取历史登录信息 """
        url = u'{0}?user_uid={1}'.format(cls.get_api('login_history')['url'], uid)
        login_history = cls.request(url, method='get', desc=u'获取历史登录信息')
        if login_history:
            for index, i in enumerate(login_history):
                ssh_history.append(i)
        return login_history

    @classmethod
    def update_login(cls, login_uuid, **kwargs):
        """ 更新登录信息: 登出时间和录像信息"""
        cls.request(
            url=cls.get_api('login_history')['url'],
            method='put',
            desc=u'更新登录信息: {0}'.format(json.dumps(kwargs, ensure_ascii=False, default=date_handler)),
            data=dict(query_string=dict(login_uuid=login_uuid), data=kwargs),
            takecare=True
        )

    @classmethod
    def backend_command(cls, data):
        """ 上传后端机器历史命令 """
        cls.request(
            url=cls.get_api('backend_command')['url'],
            desc=u'上传后端机器历史命令: {0} -- {1}'.format(data['user_name'], data['login_uuid']),
            data=data,
            takecare=True
        )

    @classmethod
    def put_command_history(cls, login_name, commands):
        """ 记录伪终端历史命令 """
        c_copy = copy.deepcopy(commands)
        for c in c_copy:
            try:
                if len(json.dumps(c)) >= 1000:  # 异常命令过滤
                    commands.remove(c)
            except UnicodeDecodeError:
                commands_list.remove(c)
        cls.request(
            url=cls.get_api('command_history')['url'],
            desc=u'记录伪终端历史命令',
            data=dict(login_name=login_name, commands_list=commands),
            takecare=True
        )

    @classmethod
    def get_command_history(cls, username):
        """ 获取伪终端历史命令 """
        url = u'{0}?login_name={1}'.format(cls.get_api('command_history')['url'], username)
        commands = cls.request(url=url, method='get', desc=u'获取终端历史命令')
        if commands:
            for command in commands if commands else []:
                commands_list.append(command)

    @classmethod
    def get_uuid(cls, uuid, source):
        """ 获取session信息 """
        url = u'{0}?uuid={1}&source={2}'.format(cls.get_api('uuid')['url'], uuid, source)
        return cls.request(url=url, method='get', desc=u'获取uuid信息')

    @classmethod
    def add_uuid(cls, connection_info, source):
        """ 记录session信息 """
        return cls.request(
                    url=cls.get_api('uuid')['url'],
                    data=dict(connection_info=connection_info, source=source),
                    desc=u'上传session信息, {0}'.format(connection_info['login_name'])
        )

    @classmethod
    def update_uuid(cls, uuid, source):
        """ 删除session信息 """
        return cls.request(
            url=cls.get_api('uuid')['url'],
            method='delete',
            data=dict(uuid=uuid, source=source),
            desc=u'删除uuid信息',
            takecare=True
        )

    @classmethod
    def del_permission(cls, key):
        return cls.request(url=cls.get_api('permission')['url'], method='delete', data=dict(key=key), takecare=True)

    @classmethod
    def get_permission(cls, key):
        return cls.request(url='{0}?key={1}'.format(cls.get_api('permission')['url'], key), method='get')

    @classmethod
    def cmdb(cls, project):
        return cls.request(url=cls.get_api('cmdb')['url'], data=dict(project=project))

    @classmethod
    def mt_cmdb(cls, host):
        return cls.request(url=cls.get_api('cmdb_mt')['url'], data=dict(host=host))

    @classmethod
    def get_redis_password(cls, query_dict):
        return cls.request(url=cls.get_api('redis_password')['url'], data=query_dict)

    @classmethod
    def host_ip(cls, host):
        result = cls.request(
            url=cls.get_api('host_search')['url'].format(host),
            method='get',
            desc=u'搜索机器: {0}'.format(host)
        )
        if result and result['num_results'] == 1:
            return result['objects'][0]['host_ip']

    @classmethod
    def get_recorder(cls, proxy_server):
        data = cls.request(
            url=cls.get_api('get_recorder')['url'].format(user_uid=proxy_server.user_info['uid']),
            desc=u'获取屏幕录像列表',
            method='get'
        )
        recorder_list = list()
        for i in data['objects']:
            if not i.get('recorder'):
                continue
            for l in i['recorder']:
                recorder_list.append(dict(
                    host_name=i['host_name'],
                    start_time=l.get('start_time', None),
                    end_time=l.get('end_time', None),
                    duration=l['duration'],
                    path=l['path']
                ))
        if recorder_list:
            proxy_server.recorder_list = recorder_list
            return recorder_list

    @classmethod
    def get_recorder_by_uuid(cls, uuid):
        data = cls.request(
            cls.get_api('get_recorder_by_uuid')['url'].format(login_uuid=uuid),
            method='get',
            desc=u'获取 {0} 录像信息'.format(uuid)
        )
        if data['objects']:
            return data['objects'][0]['recorder']
