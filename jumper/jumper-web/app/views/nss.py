# -*- coding: utf-8 -*-

import pickle

from app.main import app
from app.models import Group, User
from app.nss.nss import Nss
from app.account.user import set_user
from app.lib.app_redis import Rds
from app.nss.nss_cache import NssCache
from app.lib.view_decorator import ViewDecorator


@ViewDecorator('/nss', methods=['GET'])
def nss(data):
    if data.get('user_info'):
        return Nss.user(data['user_info'])
    elif data.get('group_info'):
        return Nss.group(data['group_info'])


@ViewDecorator('/nss/cache', methods=['GET'], response=False)
def nss_cache(data):
    if app.config.get('NSS_SWITCH') == 'on':
        return
    return NssCache().get_nss_cache(version=data['get'].get('version'), host_name=data['get'].get('host_name'))


@ViewDecorator('/nss/cache/flush', methods=['POST'])
def nss_cache_flush(data):
    """ 根据提交用户和组列表, 刷新nss缓存 """
    user_list = [User.get_by(login_name=user_name, first=True) for user_name in data['post'].get('user_list', [])]
    [set_user(user_info) for user_info in user_list if user_info]
    group_list = [Group.get_by(group_name=group_name, first=True) for group_name in data['post'].get('group_list', [])]
    group_list = [group for group in group_list if group['type'] == 'sudo']
    return NssCache(user_list=user_list, group_list=group_list).update_nss_cache()


@ViewDecorator('/nss/cache/version', methods=['GET'], args=False)
def nss_cache_version():
    data = Rds.router(readonly=True).get('nss_cache_version')
    return pickle.loads(data) if data else None
