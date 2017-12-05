# -*- coding:utf-8 -*-

import hashlib
import logging
import re
from base64 import urlsafe_b64decode as decode
from datetime import datetime

from app.lib.async import Async

from app.ssh_server.init import config


class Password:
    def __init__(self):
        pass

    @classmethod
    def check_password(cls, user_info, password, login=False):
        if user_info['lock_times'] >= 6:
            logging.warning(u'\t用户输入密码错误次数达到上限, 锁定账号:{0}'.format(user_info['login_name']))
            return False
        checked = False
        challenge_password = user_info['password']
        if len(challenge_password) == 102:
            checked = cls.check_password_sha512(challenge_password, password)
        elif len(challenge_password) == 46:
            checked = cls.check_password_sha128(challenge_password, password)
            if checked:
                # 异步更新密码至sha512加密
                config['task'].add_task(Async.convert_sha512, uid=user_info['uid'], password=password)
        if not checked and user_info['lock_times'] < 6 and login:
            user_info['lock_times'] += 1
            config['task'].add_task(Async.lock_user, user_info['login_name'], user_info['lock_times'])
        return checked

    @classmethod
    def check_old_password(cls, challenge_password, password):
        checked = False
        if len(challenge_password) == 102:
            checked = cls.check_password_sha512(challenge_password, password)
        elif len(challenge_password) == 46:
            checked = cls.check_password_sha128(challenge_password, password)
        elif len(password) == 36:
            checked = cls.check_onetime_password(password)
        return checked

    @staticmethod
    def check_password_sha128(challenge_password, password):
        challenge_password = str(challenge_password)
        password = str(password)
        challenge_bytes = decode(challenge_password[6:])
        digest = challenge_bytes[:20]
        salt = challenge_bytes[20:]
        hr = hashlib.sha1(password)
        hr.update(salt)
        return digest == hr.digest()

    @staticmethod
    def check_password_sha512(challenge_password, password):
        challenge_password = str(challenge_password)
        password = str(password)
        challenge_bytes = decode(challenge_password[6:])
        digest = challenge_bytes[:64]
        salt = challenge_bytes[64:]
        hr = hashlib.sha512(password)
        hr.update(salt)
        return digest == hr.digest()

    @staticmethod
    def check_onetime_password(password):
        # for websocket
        if Async.get_redis_password(dict(password=password)):
            return True

    @staticmethod
    def password_complex(password):
        password = str(password)
        count = 0
        r1 = re.match(r'(.*)(\d+)(.*)', password)
        r2 = re.match(r'(.*)([a-z]+)(.*)', password)
        r3 = re.match(r'(.*)([A-Z]+)(.*)', password)
        r4 = re.match(r'(.*)((\*|\?|\!|\@|\#|\$|\+|\-|\_|\%|\^|\&|\.|\=)+)(.*)', password)
        for r in (r1, r2, r3, r4):
            if r:
                count += 1
        if count >= 3:
            return True

    @classmethod
    def check_history(cls, old_password_dict, password):
        """检查历史密码"""
        if old_password_dict.get('password'):
            for x in old_password_dict['password']:
                if cls.check_old_password(x, password):
                    return True

    @staticmethod
    def password_remind(user_info):
        """
        0 :  password expired
        1 :  password reset  (将password_mtime+300天, 成为将来时间)
        2 :  password will expired in 3 days.
        """
        # 时间反序列化
        if not isinstance(user_info['password_mtime'], datetime):
            # fix 开启会话保持后, 两个窗口并行登录导致重复序列化
            user_info['password_mtime'] = datetime.strptime(user_info['password_mtime'], "%Y-%m-%d %H:%M:%S")
        between_days = datetime.now() - (user_info['password_mtime'] or datetime.now())
        count = int(config['password_ttl']) - between_days.days
        if count <= 0:
            return 0, u'您的密码已经过期,系统将强制修改密码, 回车继续...'
        elif count > 60:
            return 1, u'您最近重置过密码,系统将强制修改密码, 回车继续...'
        elif 0 < count <= 3:
            return 2, u' 您的密码还有{0}天过期, 请尽快修改密码\r\n\n'.format(count)
