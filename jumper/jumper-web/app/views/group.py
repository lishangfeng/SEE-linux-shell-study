# -*- coding: utf-8 -*-

from app.main import app
from app.models import *
from app.lib.restful import RestfulGet
from app.nss.nss_cache import NssCache
from app.lib.view_decorator import ViewDecorator
from app.account.user import user_filter, get_user


@ViewDecorator('/group', methods=['GET'])
def group_get(data):
    return RestfulGet(Group, data['get']).result


# 添加组
@ViewDecorator('/group', methods=['POST'])
def group_add(data):
    user_list = []
    if not data['post'].get('type') and data['post']['group_name'].startswith('sudo_sankuai'):
        data['post']['type'] = 'sudo'
    if data['post'].get('user_list'):
        data['post'].pop('user_list')
    gid = Group.insert(**data['post'])
    group_info = Group.get_by_id(gid)
    group_info['user_list'] = user_list
    if data.get('user_list'):
        for user_info in data['user_list']:
            user_list.append(user_info['login_name'])
            i = dict(
                    uid=user_info['uid'],
                    gid=gid,
                    type=data['post'].get('type'),
                    user_name=user_info['login_name'],
                    group_name=data['post']['group_name']
            )
            Mapper.insert(**i)
        else:
            if group_info['type'] == 'sudo' or group_info['group_name'].startswith('sudo_sankuai'):
                NssCache(user_list=data['user_list'], group_list=[group_info]).start()

    app.logger.info(u'新增分组,GroupName:{0}, Desc:{1}, GID:{2}, Users:{3}'.format(
            data['post']['group_name'],
            data['post']['desc'],
            data['post'].get('gid'),
            user_list
    ))
    return group_info


# 删除组, 删除组成员
@ViewDecorator('/group', methods=['DELETE'])
def group_delete(data):
    group_info = data['group_info']
    if data['post'].get('user_list'):
        app.logger.info(u'删除组成员,GroupName:{0}, UserList:{1}'.format(
                data['post']['group_name'],
                data['post']['user_list']
        ))
        for user_name in data['post']['user_list']:
            Mapper.delete(user_name=user_name, gid=group_info['gid'])
        user_list = [get_user(login_name=user_name) for user_name in data['post']['user_list']]
        if group_info['type'] == 'sudo' or group_info['group_name'].startswith('sudo_sankuai'):
            NssCache(user_list=user_list, group_list=[group_info]).start()
    else:
        user_list = [get_user(login_name=user_name) for user_name in Mapper.get_by(group_name=group_info['group_name'])]
        app.logger.info(u'删除分组,GroupName:{0}'.format(data['post']['group_name']))
        group_name = group_info['group_name']
        Sudo.delete(role='group', role_name=group_name)
        Auth.delete(role='group', role_id=data['group_info']['gid'])
        Mapper.delete(group_name=group_name)
        Group.delete(group_name=group_name)
        if group_info['type'] == 'sudo' or group_name.startswith('sudo_sankuai'):
            NssCache(user_list=user_list).start()


# 添加组成员
@ViewDecorator('/group', methods=['PUT'])
def group_update(data):
    group_info = data['group_info']
    app.logger.info(u'添加组成员,GroupName:{0}, UserList:{1}'.format(
            data['post']['group_name'],
            data['post']['user_list']
    ))
    for user_info in data['user_list']:
        i = dict(
                uid=user_info['uid'],
                gid=group_info['gid'],
                user_name=user_info['login_name'],
                group_name=group_info['group_name'],
                type=group_info['type']
        )
        Mapper.insert(**i)
    if data['user_list']:
        if group_info['type'] == 'sudo' or group_info['group_name'].startswith('sudo_sankuai'):
            NssCache(user_list=data['user_list'], group_list=[group_info]).start()
    data['group_info']['user_list'] = [i['user_name'] for i in Mapper.get_by(gid=data['group_info']['gid'])]
    return data['group_info']


# 获取组成员
@ViewDecorator('/group/<string:name>', methods=['GET'])
def group_get_by_name(data):
    group_info = Group.get_by(group_name=data['get']['name'])
    if not group_info:
        return
    group_info = group_info[0]
    group_info['user_list'] = [i['user_name'] for i in Mapper.get_by(gid=group_info['gid'])]
    return group_info


# 获取组成员
@ViewDecorator('/group/detail/<string:name>', methods=['GET'])
def group_member_detail(data):
    group_info = [i['uid'] for i in Mapper.get_by(group_name=data['get']['name'])]
    user_list = User.query_in(key='uid', in_list=group_info, show="login_time,name,organization,login_name,enable")
    return [user_filter(i) for i in user_list]
