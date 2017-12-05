# -*- coding: utf-8 -*-

import datetime
from threading import Thread

from app.main import app
from app.models import Session
from app.lib.app_redis import Rds
from app.lib.error_define import RedisExceptionError
from app.account.user import user_organization


class UUID:
    def __init__(self):
        pass

    @staticmethod
    def get(source, uuid):
        try:
            con = Rds.router(source=source).exist_uuid(uuid)
        except RedisExceptionError:
            # 如果source是mt则切换到dp, 如果source是其它则切换到默认
            if source == 'MT':
                app.logger.warning(u'检查uuid是否存在, 异常, 切换到DP缓存')
                try:
                    con = Rds.router(source='DP').exist_uuid(uuid)
                    app.logger.warning(u'检查uuid是否存在, 异常, backup DP缓存同时失效')
                except RedisExceptionError:
                    con = None
            else:
                app.logger.warning(u'检查uuid是否存在, 异常, 切换到default缓存')
                try:
                    con = Rds.router().exist_uuid(uuid)
                except RedisExceptionError:
                    app.logger.warning(u'检查uuid是否存在, 异常, backup default缓存同时失效')
                    con = None
        return con

    @staticmethod
    def set(source, info):
        try:
            con = Rds.router(source=source).set_uuid(info)
        except RedisExceptionError:
            # 如果source是mt则切换到dp, 如果source是其它则切换到默认
            if source == 'MT':
                app.logger.warning(u'鉴权uuid, 异常, 切换到DP缓存')
                try:
                    con = Rds.router(source='DP').set_uuid(info)
                except RedisExceptionError:
                    app.logger.warning(u'鉴权uuid, 异常, backup DP缓存同时失效')
                    con = None
            else:
                try:
                    con = Rds.router().set_uuid(info)
                except RedisExceptionError:
                    app.logger.warning(u'鉴权uuid, 异常, backup default缓存同时失效')
                    con = None
        return con

    @staticmethod
    def delete(source, uuid):
        try:
            con = Rds.router(source=source).del_uuid(uuid)
        except RedisExceptionError:
            # 如果source是mt则切换到dp, 如果source是其它则切换到默认
            if source == 'MT':
                app.logger.warning(u'清理uuid, 异常, 切换到DP缓存')
                try:
                    con = Rds.router(source='DP').del_uuid(uuid)
                except RedisExceptionError:
                    app.logger.warning(u'清理uuid, 异常, backup DP缓存同时失效')
                    con = None
            else:
                app.logger.warning(u'清理uuid, 异常, 切换到default缓存')
                try:
                    con = Rds.router().del_uuid(uuid)
                except RedisExceptionError:
                    app.logger.warning(u'清理uuid, 异常, backup default缓存同时失效')
                    con = None
        return con


class SessionFilter(Thread):
    """ 异步更新金融组用户会话超时 """
    def __init__(self, source, info):
        Thread.__init__(self)
        self.info = info
        self.source = source
        self.daemon = True
        self.start()

    def run(self):
        with app.app_context():
            if isinstance(self.info, dict):
                # 更新会话过期时间, 同时记录session
                is_session_expire = 0
                for x in app.config.get('SESSION_EXPIRE', []):
                    expire = x['expire']
                    organization = x['organization']
                    if user_organization(self.info['login_name'], organization):
                        is_session_expire += 1
                        if Rds.router(source=self.source).exist_uuid(self.info['uuid']):
                            if Rds.router(source=self.source).session_expire(self.info['uuid'], expire * 60):
                                app.logger.warning(u'{0}为特殊组织架构[{1}]用户, 会话超时时间被设置成{2}分钟'.format(
                                        self.info['login_name'], organization, expire))
                            else:
                                app.logger.warning(u'{0}为特殊组织架构[{1}]用户, 会话超时时间被设置成{2}分钟, 失败!!!'.format(
                                        self.info['login_name'], organization, expire))
                        self.save_session(expire)  # 保存会话信息
                        break
                else:
                    if not is_session_expire:
                        self.save_session(24 * 60)  # 判断如果不属于特殊组, 则默认24小时
            else:
                # 清理uuid后关闭session记录的logout_time
                Session.update(dict(uuid=self.info), dict(logout_time=datetime.datetime.now()))

    def save_session(self, ttl):
        session_info = dict(
            ttl=ttl * 60,
            name=self.info['name'],
            uuid=self.info['uuid'],
            user_id=self.info['user_id'],
            login_name=self.info['login_name'],
            login_time=self.info['login_time'],
            pid=self.info['pid'],
            client_port=self.info['client_port'],
            client_ip=self.info['client_ip'],
            server_name=self.info['server_name']
        )
        if not Session.get_by(uuid=session_info['uuid'], first=True):
            Session.insert(**session_info)
