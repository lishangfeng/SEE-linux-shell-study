#!/bin/env python
# -*- coding: utf-8 -*-

import uuid
import time
import pickle
import datetime  # eval反序列化也需要

from app.main import app
from threading import Thread
from app.nss.nss import Nss
from app.lib.app_redis import Rds
from app.lib.error_define import res
from app.nss.utlis import save_local_nss_cache_all, read_local_nss_cache_all
from app.nss.utlis import save_local_nss_cache, del_local_nss_cache, read_local_nss_cache


class NssCache(Thread):
    def __init__(self, user_list=None, group_list=None, smoke=False):
        Thread.__init__(self)
        self.daemon = True
        self.smoke = smoke
        self.user_list = user_list or list()
        self.group_list = group_list or list()
        self.version_uuid = str(uuid.uuid4())
        self.version_number = int(app.config.get('NSS_CACHE_VERSION', 50))
        self.nss_cache_version = Rds.router(readonly=True).get('nss_cache_version')
        self.nss_cache_version = pickle.loads(self.nss_cache_version) if self.nss_cache_version else list()

    def run(self):
        with app.app_context():
            self.update_nss_cache()

    def update_nss_cache(self):
        self.user_list = [user_info for user_info in self.user_list if user_info]
        self.group_list = [group_info for group_info in self.group_list if group_info]
        if not self.user_list and not self.group_list:
            return False
        else:
            begin = time.time()
            app.logger.info(u'开始更新nss缓存')

        # 更新用户nss缓存
        for nss_user in [Nss.user(user_info) for user_info in self.user_list]:
            try:
                Rds.router().hset('nss_cache_user', nss_user['pw_name'], pickle.dumps(nss_user, protocol=True))
                app.logger.debug(u'{0} 更新nss-user: {1}'.format(self.version_uuid, nss_user['pw_name']))
            except Exception as e:
                app.logger.error(u'{0} 更新nss-user{1} 失败:{2}'.format(self.version_uuid, nss_user['pw_name'], str(e)))
        # 更新组nss缓存
        for nss_group in [Nss.group(group_info) for group_info in self.group_list]:
            try:
                Rds.router().hset('nss_cache_group', nss_group['gr_name'], pickle.dumps(nss_group, protocol=True))
                app.logger.debug(u'{0} 更新nss-group: {1}'.format(self.version_uuid, nss_group['gr_name']))
            except Exception as e:
                app.logger.error(u'{0} 更新nss-group{1} 失败:{2}'.format(self.version_uuid, nss_group['gr_name'], str(e)))

        # 更新nss-version
        if self.smoke:
            app.logger.info(u'{0} 重置nss缓存版本库'.format(self.version_uuid))
            for version in self.nss_cache_version:
                del_local_nss_cache(version['version'])
            Rds.router().delete('nss_cache')

            self.nss_cache_version = list()
            self.nss_cache_version.append(dict(
                version=self.version_uuid,
                create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_list=list(),
                group_list=list(),
                update=True,
                size=0
            ))
        else:
            self.nss_cache_version.append(dict(
                version=self.version_uuid,
                create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_list=[user_info['login_name'] for user_info in self.user_list],
                group_list=[group_info['group_name'] for group_info in self.group_list],
                update=False,
                size=0
            ))

            for version in self.nss_cache_version:
                version['update'] = False

            if len(self.nss_cache_version) > self.version_number:
                self.nss_cache_version = self.nss_cache_version[-self.version_number:]

        Rds.router().set('nss_cache_version', pickle.dumps(self.nss_cache_version, protocol=True))
        app.logger.info(u'{0} 更新nss缓存成功, 一共耗时:{1}'.format(self.version_uuid, time.time() - begin))
        return self.nss_cache_version[-1]

    def update_nss_version(self, nss_version):
        # 计算版本缓存
        nss_user = dict()
        nss_group = dict()

        for index, version in enumerate(self.nss_cache_version[::-1]):
            nss_cache = dict(version=self.nss_cache_version[-1]['version'], group=list(), user=list())
            if index >= self.version_number:
                Rds.router().hdel('nss_cache', version['version'])
                continue

            for user_name in version['user_list']:
                if not nss_user.get(user_name):
                    nss_user[user_name] = pickle.loads(Rds.readonly().hget('nss_cache_user', user_name))
            for group_name in version['group_list']:
                if not nss_group.get(group_name):
                    nss_group[group_name] = pickle.loads(Rds.readonly().hget('nss_cache_group', group_name))

            if nss_version == version['version']:
                version['update'] = True
                nss_cache["user"].extend(nss_user.values())
                nss_cache["group"].extend(nss_group.values())
                version_data = res(nss_cache, response_class=False)
                Rds.router().hset('nss_cache', version['version'], version_data)
                save_local_nss_cache(version_data, version['version'])
                version['size'] = len(version_data)
                return version_data

    def get_nss_cache(self, version=None, host_name=None):
        """
            从缓存中获取nss数据
            1: 根据version更新增量
            2: 如果未匹配到version, 则更新全量
            len: 标志本地缓存大小和redis缓存大小是否一致，不一致就更新
        """
        app.logger.info(u'客户端: {0}, {1}'.format(host_name, version))
        if not self.nss_cache_version:
            app.logger.warning(u'服务端没有nss缓存')
            return False

        if self.nss_cache_version[-1]['version'] == version:
            app.logger.debug(u'{0} 已经是最新版本, 无需更新'.format(host_name))
            return res(dict(version=version, group=list(), user=list()), response_class=False)
        else:
            version_info = dict()
            last_version = self.nss_cache_version[-1]['version']
            for n, nss_version in enumerate(self.nss_cache_version):
                if nss_version['version'] == version:
                    version_info = self.nss_cache_version[n+1]
                    version = version_info['version']
                    app.logger.info(u'修正版本, {0} -> {1}'.format(nss_version['version'], version))
                    break

        if version_info:
            if not version_info['update']:
                app.logger.info(u'版本未缓存, 重新计算 {0}'.format(version))
                version_data = self.update_nss_version(version)
                Rds.router().set('nss_cache_version', pickle.dumps(self.nss_cache_version, protocol=True))
                return version_data

            app.logger.info(u'获取增量版本 {0}'.format(version))
            version_data = read_local_nss_cache(version)

            if version_data and version_info['size'] == len(version_data):
                return version_data

            app.logger.info(u'本地缓存失效, 尝试从redis获取')
            version_data = Rds.router(readonly=True).hget('nss_cache', version)
            if version_data:
                app.logger.info(u'从redis获取成成功')
                save_local_nss_cache(version_data, version)
                return version_data

            app.logger.info(u'从redis获取失败, 重新计算版本 {0}'.format(version))
            return self.update_nss_version(version)
        else:
            app.logger.debug(u'获取全量数据 {0}'.format(last_version))
            version_data = read_local_nss_cache_all(last_version)                        # 从本地读取全量
            if version_data:
                return version_data

            if Rds.router(readonly=True).get('nss_cache_all_version') == last_version:   # 从redis读取全量
                version_data = Rds.router(readonly=True).get('nss_cache_all')
            if version_data:
                app.logger.debug(u'从redis读取全量缓存成功')
                return save_local_nss_cache_all(version_data, last_version)

            else:                                                                        # 重新计算全量
                app.logger.debug(u'从redis读取失败, 重新计算')
                version_data = dict(
                    version=last_version,
                    user=list(),
                    group=list()
                )
                for user_info in Rds.readonly().hgetall('nss_cache_user').values():
                    version_data['user'].append(pickle.loads(user_info))
                for group_info in Rds.readonly().hgetall('nss_cache_group').values():
                    version_data['group'].append(pickle.loads(group_info))

                version_data = save_local_nss_cache_all(res(version_data, response_class=False), last_version)
                Rds.router().set('nss_cache_all', version_data)
                Rds.router().set('nss_cache_all_version', last_version)
                return version_data
