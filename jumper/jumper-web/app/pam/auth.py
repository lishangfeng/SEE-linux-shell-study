# -*- coding: utf-8 -*-

from flask import current_app as app
from app.pam.session import UUID
from app.lib.app_redis import Rds
from app.pam.auth_permit import AuthPermit
from app.lib.error_define import res
from app.host.host_cache import HostCache
from app.account.password import Password
from app.lib.error_define import RedisExceptionError


class AccountCheck:
    def __init__(self, data):
        self.user_info = data['user_info']
        self.data = data

    def check_password(self):
        password = self.data['post']['password']
        connection_info = None
        # 验证账号是否离职
        if not self.user_info['enable']:
            return res(code=4, msg='account {0} is disabled, not permit to login'.format(self.user_info['login_name']))
        # 密码为数字
        if isinstance(password, int):
            return res(code=5, msg='password is pure digit:{0}, not allowed'.format(password))
        # 验证账号密码
        if len(password.split('-')) == 5 and len(password) == 36:
            connection_info = UUID.get(source=self.user_info['source'], uuid=password)
            if not connection_info:
                return res(code=3, msg='account session has expired:{0}'.format(password))
        elif not Password.check_password(self.user_info['password'], password):
            return res(code=2, msg='password is not correct')
        return connection_info

    def check_account(self):
        # 验证账号是否离职
        if not self.user_info['enable']:
            return res(code=4, msg='account {0} is disabled, not permit to login'.format(self.user_info['login_name']))
        if self.user_info.get('db_error'):
            app.logger.warning(
                u'mysql连接故障，自动忽略权限校验 校验主机,:{0}, 账号:{1}'.format(self.data['get']['host_ip'], self.user_info['login_name']))
            return True

        # 根据机器ip获得location位置
        # 验证授权
        host_info = HostCache.fetch_host(self.data['get']['host_ip'])
        if not host_info:
            return res(code=1, msg='this host not exist in jumper system, permission deny')
        if host_info['corp'] == 'meituan':
            if not AuthPermit(self.data).auth():
                if self.data['get']['login']:  # 登陆和非登陆验证account字段
                    permission_deny = dict(
                        login_name=self.user_info['login_name'],
                        host_ip=self.data['get']['host_ip'],
                        message=u'您没有权限登录该机器! 如还有疑问请联系SRE.'
                    )
                    try:
                        Rds.router().no_permission(permission_deny)
                    except RedisExceptionError:
                        pass
                    return res(code=1, msg='account {0} dont have permission to access this host'.format(
                            self.user_info['login_name']))
            else:
                return True
        elif host_info['corp'] == 'dianping':
            if host_info['pdl'] in app.config.get('AUTH_PDL'):
                if not AuthPermit(self.data).auth():
                    if self.data['get']['login']:  # 登陆和非登陆验证account字段
                        permission_deny = dict(
                                login_name=self.user_info['login_name'],
                                host_ip=self.data['get']['host_ip'],
                                message=u'您没有权限登录该机器! 如还有疑问请联系SRE.'
                        )
                        try:
                            Rds.router().no_permission(permission_deny)
                        except RedisExceptionError:
                            pass
                        return res(code=1, msg='account {0} dont have permission to access this host'.format(
                                self.user_info['login_name']))
                    else:
                        return False
            return True
        else:
            return False
