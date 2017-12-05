# -*- coding:utf-8 -*-

import os
from flask import current_app as app
from datetime import datetime

from app.models import User
from app.lib.app_redis import Rds


def flush_user(user_list=None):
    st = datetime.now()
    user_list = user_list or User.get_by()
    [Rds.router().set_user(user_info) for user_info in user_list]
    app.logger.info(u'刷入用户数量: {0}, 耗时: {1}'.format(len(user_list), datetime.now() - st))
    return user_list


def password(user_info):
    return dict(
        pw_name=user_info['login_name'],
        pw_passwd='x',
        pw_uid=user_info['uid'],
        pw_gid=user_info['gid'],
        pw_gecos=user_info['desc'],
        pw_dir=user_info['home_dir'],
        pw_shell=user_info['shell']
    )


def shadow(user_info):
    return dict(
        sp_namp=user_info['login_name'],
        sp_pwdp=user_info['password'],
        sp_lstchg=16034,
        sp_min=0,
        sp_max=99999,
        sp_warn=7,
        sp_inact=None,
        sp_expire=None,
        sp_flag=None
    )


def group(group_info, _type='group'):
    if _type == 'user':
        return dict(
            gr_name=group_info['login_name'],
            gr_passwd='x',
            gr_gid=group_info['gid'],
            gr_mem=[group_info['login_name']],
        )
    else:
        return dict(
            gr_name=group_info['group_name'],
            gr_passwd='x',
            gr_gid=group_info['gid'],
            gr_mem=[],
        )


# nss 本地缓存
def save_local_nss_cache(nss_cache_data, version):
    try:
        if os.path.exists(app.config.get('NSS_CACHE_LOCAL_DIR')):
            open(os.path.join(app.config.get('NSS_CACHE_LOCAL_DIR'), version), 'wb').write(nss_cache_data)
            app.logger.debug(u'写入本地缓存成功 {0}'.format(version))
        return nss_cache_data
    except Exception as e:
        app.logger.error(u'写入本地缓存失败: {0}, {1}'.format(version, str(e)))


def del_local_nss_cache(version):
    try:
        if os.path.exists(os.path.join(app.config.get('NSS_CACHE_LOCAL_DIR'), version)):
            os.remove(os.path.join(app.config.get('NSS_CACHE_LOCAL_DIR'), version))
    except Exception as e:
        app.logger.error(u'删除本地缓存失败: {0}, {1}'.format(version, str(e)))


def read_local_nss_cache(version):
    try:
        if os.path.exists(os.path.join(app.config.get('NSS_CACHE_LOCAL_DIR'), version)):
            data = open(os.path.join(app.config.get('NSS_CACHE_LOCAL_DIR'), version), 'r').read().strip()
            app.logger.debug(u'读取本地缓存成功 {0}'.format(version))
            return data
    except Exception as e:
        app.logger.error(u'读取本地缓存失败: {0}, {1}'.format(version, str(e)))


# Nss 全量本地缓存
def save_local_nss_cache_all(nss_cache_data, version):
    try:
        if os.path.exists(app.config.get('NSS_CACHE_LOCAL_DIR')):
            open(os.path.join(app.config.get('NSS_CACHE_LOCAL_DIR'), 'NSS_CACHE_ALL'), 'wb').write(nss_cache_data)
            open(os.path.join(app.config.get('NSS_CACHE_LOCAL_DIR'), 'NSS_VERSION'), 'wb').write(version)
            app.logger.debug(u'写入本地全量缓存成功 {0}'.format(version))
    except Exception as e:
        app.logger.error(u'写入本地缓存失败: {0}, {1}'.format(version, str(e)))
    return nss_cache_data


def read_local_nss_cache_all(version):
    try:
        if open(os.path.join(app.config.get('NSS_CACHE_LOCAL_DIR'), 'NSS_VERSION'), 'r').read().strip() == version:
            data = open(os.path.join(app.config.get('NSS_CACHE_LOCAL_DIR'), 'NSS_CACHE_ALL'), 'r').read().strip()
            app.logger.debug(u'读取本地全量缓存成功 {0}'.format(version))
            return data
    except Exception as e:
        app.logger.error(u'读取本地缓存失败: {0}, {1}'.format(version, str(e)))
