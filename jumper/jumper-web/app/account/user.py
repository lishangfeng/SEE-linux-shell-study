# -*- coding:utf-8 -*-

from datetime import datetime
from flask import g, session
from flask import current_app as app

from app.models import User
from app.lib.app_redis import Rds
from app.lib.http_client import http_client
from app.lib.error_define import SupportError

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def set_user(user_info):
    if user_info:
        return Rds.router().set_user(user_info)


def get_user(**kwargs):
    if kwargs.get('uid'):
        return User.get_by_id(kwargs['uid'])
    elif kwargs.get('login_name'):
        user_info = Rds.router(readonly=True).get_user(kwargs['login_name'])
        if user_info:
            return user_info
        user_info = User.get_by(login_name=kwargs['login_name'], first=True)
        if user_info:
            user_info = Rds.router().set_user(user_info)
            return user_info
    else:
        return Rds.router(readonly=True).get_user()


def get_user_info(**kwargs):
    if kwargs.get('uid'):
        user_info = User.query.filter_by(id=kwargs['uid']).first()
        if user_info:
            return user_info.to_dict()
        else:
            raise SupportError(u'该用户不存在{0}'.format(kwargs.get('uid')))

    if kwargs.get('login_name'):
        user_info = User.query.filter_by(login_name=kwargs['login_name']).first()
        if user_info:
            return user_info.to_dict()
        else:
            raise SupportError(u'该用户不存在{0}'.format(kwargs.get('login_name')))

    if session.get('CAS_USERNAME'):
        user_info = User.query.filter_by(login_name=session.get('CAS_USERNAME')).first()
        if user_info:
            return user_info.to_dict()
        else:
            return get_user_auth(session.get('CAS_USERNAME'))

    if hasattr(g, 'token'):
        return g.token

    if hasattr(g, 'sso'):
        return g.sso

    raise SupportError(u'未登录')


def get_user_auth(user_name):
    """ 从企业获取员工信息 """
    try:
        url = 'http://ops.auth.dp/userService/getByAd?ad={0}'
        outsource_url = 'http://ops.auth.dp/userService/queryOuterUserByAd?ad={0}'
        result = http_client(url.format(user_name), timeout=10).json()
        if not result:
            result = http_client(outsource_url.format(user_name), timeout=10).json()
            if not result:
                app.logger.error(u'从企业系统获取用户信息({0})失败: {0}'.format(user_name))
                raise SupportError(u'从企业系统获取用户信息失败')
        user_info = result['user']
    except Exception, e:
        app.logger.error(u'从企业系统获取用户信息({0})失败: {1}'.format(user_name, str(e)))
        raise SupportError(u'从企业系统获取用户信息失败: {0}'.format(str(e)))
    if user_info['locationName'] != "上海":
        user_info['source'] = 'MT'

    birthday = None
    try:
        birthday = datetime.strptime(user_info['birthDay'], "%Y-%m-%d %H:%M:%S.%f")
    except:
        pass

    return dict(
            number=user_info['employeeId'],
            login_name=user_info['ad'],
            name=user_info['employeeName'],
            organization=user_info['organizationName'],
            source=user_info['source'],
            email=user_info['email'],
            mobile=user_info['mobileNo'],
            home_dir='/home/{0}'.format(user_name),
            shell='/bin/bash',
            birthday=birthday,
            enable=1
    )


def user_filter(user_info):
    try:
        user_info.pop('password')
        user_info.pop('public_key')
        user_info.pop('key')
        user_info.pop('old_password_dict')
        user_info.pop('salt')
    except KeyError:
        pass
    return user_info


def user_cache(user_info):
    return dict(
        name=user_info['login_name'],
        uid=user_info['uid']
    )


def user_source(user_name):
    user_info = User.get_by(login_name=user_name, first=True)
    return user_info.get('source', 'mt').lower() if user_info else 'mt'


# 查询员工组织架构
def user_organization(user_name, organization):
    url = 'https://ops.sankuai.com/api/users/profile?user={0}'
    headers = {'Authorization': 'Bearer d1b3ef487d9b8ca5a817443d77f217302c038b81'}
    try:
        result = http_client(url.format(user_name), headers=headers).json()['org_path']
        if organization in result:
            return True
    except Exception as e:
        app.logger.error(u'调用接口出错: 用户{0}, 报错:{1}'.format(user_name, str(e)))
