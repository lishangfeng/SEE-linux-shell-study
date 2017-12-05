#!/bin/env python
# -*- coding:utf-8 -*-
# 权限控制

from flask import g, session

from flask import current_app as app
from app.account.user import get_user_info
from app.lib.error_define import PermissionError


class Permission(object):
    def __init__(self):
        pass

    @staticmethod
    def filter(filter_type):
        data = dict(
                auth=[
                    'auth_add',
                    'auth_delete',
                    'auth_update'
                ],
                sudo=[
                    'sudo_add',
                    'sudo_delete',
                    'sudo_update'
                ],
                group=[
                    'group_add',
                    'group_delete',
                    'group_update'
                ],
                host=[
                    'host_add',
                    'host_delete',
                    'host_update'
                ],
                user=[
                    'user_add',
                    'user_delete',
                    'user_update',
                    'user_update_uid',
                    # 'user_reset_password' web端自己重置自己
                ],
                nss=[
                    'nss_cache_flush'
                ],
                jumper=[
                    'clean_up',
                    'heartbeat',
                    'clean_up_v2',
                    'heartbeat_v2',
                    'jumper_user_get2',
                    'jumper_user_get',
                    'jumper_update_user',
                    'jumper_update_password',
                    'lock_user',
                    'unlock_user',
                    'login_history_add',
                    'login_history_update',
                    'jumper_uuid_set',
                    'jumper_uuid_get',
                    'jumper_uuid_del',
                    'jumper_history_add',
                    'add_command',
                    'permission_del',
                    'permission_get',
                    'jumper_host_corp',
                    'save_script',
                    'delete_script'
                ],
        )
        if not app.config.get('SSO_AUTH'):
            return True
        else:
            function_name = list()
            [function_name.extend(i) for i in data.values()]
        if filter_type in function_name:
            if g.get('token'):
                return True
            elif session.get('CAS_USERNAME') and get_user_info().get('role') in app.config['ADMIN_ROLE']:
                return True
            raise PermissionError(u'Hi 您没有权限操作')
