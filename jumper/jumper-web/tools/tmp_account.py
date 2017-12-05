# -*- coding: utf-8 -*-

from app.main import app
from app.models import *
from flask_script import Command
from datetime import timedelta, datetime
from app.account.password import Password
from app.account.user import get_user
from app.nss.nss_cache import NssCache
from app.lib.notice import Notice


class TMPAccount(Command):
    @classmethod
    def run(cls):
        with app.app_context():
            login_name = 'tmp.zhongjin'
            email = 'alex.wan@dianping.com'
            user_info = dict(
                    login_name=login_name,
                    name=login_name,
                    email=email,
                    source='DP',
                    enable=1
            )
            if User.get_by(login_name=login_name):
                print
                print u'\t账户已存在'
                print
                return
            # 修改时间将来时, 作为重置密码后的标志
            user_info['password_mtime'] = datetime.now() + timedelta(days=300)
            # 初始化密码
            password = Password.random_password()
            password_sha1, salt = Password.get_password(password=password)
            user_info.update(dict(password=password_sha1, salt=salt))
            # 写数据库
            user_info = User.get_by_id(User.insert(**user_info))
            # 更新gid
            User.update(dict(uid=user_info['uid']), dict(gid=user_info['uid']))
            # 开始更新缓存
            user_info = get_user(login_name=login_name)
            NssCache(user_list=[user_info]).start()
            # 发送消息给注册用户
            message = u"""Hi 您的跳板机账号申请成功, 请及时修改密码!
                    登陆账号: {0}
                    初始密码: {1}
            使用指南: """.format(login_name, password)
            message += app.config['WIKI']
            Notice(message, email)
