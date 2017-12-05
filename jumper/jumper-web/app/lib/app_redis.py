# -*- coding:utf-8 -*-

import json
import copy
import redis
import pickle
import datetime    # eval反序列化转换需要
import traceback
from types import MethodType
from random import randint
from functools import wraps

from flask import current_app as app
from app.lib.error_define import RedisExceptionError
from app.lib.error_define import RedisError

redis_map = dict()
Redis_Error = ['set_uuid', 'get_uuid', 'del_uuid', 'exist_uuid', 'lock_times', 'get_host', 'no_permission']


def wrapper(method):
    @wraps(method)
    def wrapped(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            # 对于uuid的异常我们抛出去, 让其它函数捕获
            msg = 'function[{0}] occurred error --> {1}'.format(method.__name__, str(e))
            # 先注释, 避免读写分离影响
            if method.__name__ in Redis_Error:
                raise RedisExceptionError(msg)
            app.logger.warning(msg)
            raise RedisError(msg)
    return wrapped


class AppRedis(redis.StrictRedis):

    def __init__(self, *args, **kwargs):
        redis.StrictRedis.__init__(self, *args, **kwargs)
        self.uuid = 'login_uuid_{0}'
        self.token_uuid = 'token_uuid_{0}'
        self.onetime_uuid = 'onetime_uuid_{0}'
        self.lock = 'password_retry:{0}'
        self.ssh_ttl = 60
        self.token_ttl = 10 * 60
        self.uuid_ttl = 24 * 3600
        self.command_ttl = 30 * 24 * 3600

    def __getattribute__(self, item):
        """ 对redis的操作函数进行一层封装, 捕获异常 """
        attr = super(AppRedis, self).__getattribute__(item)
        if type(attr) == MethodType:
            attr = wrapper(attr)
        return attr

    def get_uuid(self, uuid):
        """ 获取用户session信息, 后端机器登陆鉴权接口使用 """
        self.expire(self.uuid.format(uuid), self.uuid_ttl)
        return self.hgetall((self.uuid.format(uuid)))

    def set_uuid(self, uuid):
        """ 用户信息写入session, 伪终端插入session接口使用 """
        [self.hset(self.uuid.format(uuid['uuid']), k, v) for k, v in uuid.items()]
        return self.expire(self.uuid.format(uuid['uuid']), self.uuid_ttl)

    def set_token(self, user_info):
        """ 生成web终端验证码, 前端跳板机登陆code生成接口使用 """
        [self.hset(self.token_uuid.format(user_info['uuid']), k, v) for k, v in user_info.items()]
        return self.expire(self.token_uuid.format(user_info['uuid']), self.token_ttl)

    def check_token(self, code):
        """ 验证web终端验证码, 前端跳板机登陆鉴权接口使用 """
        code = self.exists(code)
        if code:
            self.delete(code)
        return code

    def onetime_password(self, uuid):
        """ 获取用户redis一次性密码, 前端机器登陆鉴权接口使用 """
        password = self.exists(self.onetime_uuid.format(uuid))
        if password:
            self.delete(self.onetime_uuid.format(uuid))
        return password

    def del_uuid(self, uuid):
        """ 清理用户session, 伪终端退出清理session接口使用"""
        return self.delete(self.uuid.format(uuid))

    def session_expire(self, uuid, ttl):
        """
        会话过滤器, 例如对金融组员会话超时设置为15分钟等等
        """
        return self.expire(self.uuid.format(uuid), ttl)

    def exist_uuid(self, uuid):
        """ 验证用户session, 伪终端提醒用户会话过期接口使用"""
        return self.exists((self.uuid.format(uuid)))

    def get_user(self, login_name=None):
        """ 从缓存取用户信息 """
        if login_name:
            data = self.hget('user_list', login_name)
            return eval(data) if data else dict()
        else:
            data = self.hgetall('user_list')
            return [eval(user_info) for user_info in data.values()] if data else list()

    def set_user(self, user_info):
        """ 缓存用户信息 """
        self.hset('user_list', user_info['login_name'], user_info)
        app.logger.debug(u'缓存用户 {0}'.format(user_info['login_name']))
        return user_info

    def del_user(self, login_name):
        """ 删除缓存的用户信息 """
        app.logger.debug(u'删除缓存 {0}'.format(login_name))
        self.hdel('user_list', login_name)

    def get_session(self):
        """ 查看所有session接口 """
        keys = list()
        data = list()
        [keys.append(k) for k in self.scan_iter(match=self.uuid.format('*'), count=500)]
        [data.append(self.hgetall(i)) for i in keys]
        [u.update(dict(ttl=self.ttl(self.uuid.format(u['uuid'])))) for u in data if u]
        return data

    def count_session(self):
        """ 会话数统计 """
        keys = list()
        user = set()
        [keys.append(k) for k in self.scan_iter(match=self.uuid.format('*'), count=500)]
        [user.add(self.hget(i, 'name')) for i in keys]
        return len(user), len(keys)

    def set_history(self, payload):
        """ 记录用户登录历史 """
        self.hset('commands_history', payload['login_name'], pickle.dumps(payload['commands_list']))
        return True

    def get_history(self, login_name):
        """ 获取用户登录历史 """
        """
            伪终端有时候记录了用户输入的无法解码的(latin1)数据, 剔除此类记录
        """
        command = self.hget('commands_history', login_name)
        if command:
            commands = pickle.loads(command)
            c_copy = copy.deepcopy(commands)
            for c in c_copy:
                try:
                    json.dumps(c)
                except UnicodeDecodeError:
                    commands.remove(c)
            return commands
        return list()

    def no_permission(self, uuid):
        """ 提示用户无权限登录目标机器 """
        temp = '{0}:{1}'.format(uuid['login_name'], uuid['host_ip'])
        self.set(temp, uuid['message'])
        return self.expire(temp, self.ssh_ttl)

    def lock_user(self, login_name, ttl):
        times = self.incr(self.lock.format(login_name))
        if times and self.expire(self.lock.format(login_name), ttl):
            return times

    def lock_times(self, login_name):
        return self.get(self.lock.format(login_name))

    def unlock_user(self, login_name):
        return self.delete(self.lock.format(login_name))

    def set_host(self, host):
        self.hset('host_list', host['host_ip'], pickle.dumps(host))
        app.logger.debug(u'缓存主机 {0}'.format(host['host_name']))
        return host

    def del_host(self, host_ip):
        self.hdel('host_list', host_ip)
        app.logger.debug(u'删除缓存 {0}'.format(host_ip))

    def del_host_list(self):
        self.delete('host_list')
        app.logger.debug(u'删除所有host缓存')

    def get_host(self, host_ip=None):
        if host_ip:
            data = self.hget('host_list', host_ip)
            return pickle.loads(data) if data else None
        else:
            data = self.hgetall('host_list')
            return [pickle.loads(host_info) for host_info in data.values()] if data else list()

    def all_sudo_key(self):
        return [k for k in self.scan_iter(match='sudo_*', count=500)]

    def get_sudo(self, label):
        return self.get('sudo_*'.format(label))

    def set_sudo(self, label_key, data):
        self.set('sudo_{0}'.format(label_key), data)

    def del_sudo(self, label_key):
        self.delete('sudo_{0}'.format(label_key))


class Rds:

    def __init__(self):
        pass

    @classmethod
    def router(cls, source=None, **kwargs):
        if kwargs.get('readonly'):
            return cls.readonly()
        else:
            if source is None:
                return redis_map['default']
            elif source.lower() == 'dp':  # 存在上海即读取上海, 不然读取北京
                return redis_map['dp'] if 'dp' in redis_map else redis_map['default']
            elif source.lower() == 'mt':  # 存在mt即读取mt, 不存在即读取默认
                return redis_map['default']
            else:
                return redis_map['default']

    @classmethod
    def readonly(cls):
        # 从连接池中取随机
        i = randint(0, len(redis_map['readonly']) - 1)
        return redis_map['readonly'][i]
