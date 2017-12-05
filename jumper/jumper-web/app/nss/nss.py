#!/bin/env python
# -*- coding:utf-8 -*-

from app.models import Mapper
from app.nss.utlis import *


class Nss:
    def __init__(self):
        pass

    @classmethod
    def user(cls, user_info):
        mapper_list = Mapper.get_by(uid=user_info['uid'], type='sudo')
        data = dict(group=dict())
        data.update(password(user_info))
        data['group'][user_info['gid']] = group(user_info, _type='user')
        for i in mapper_list:
            data['group'][i['gid']] = group(i)
            data['group'][i['gid']]['gr_mem'].append(user_info['login_name'])
        return data

    @classmethod
    def group(cls, group_info):
        if group_info.get('uid'):
            return group(group_info, _type='user')
        else:
            data = group(group_info)
            for i in Mapper.get_by(gid=group_info['gid']):
                data['gr_mem'].append(i['user_name'])
            return data
