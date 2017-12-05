# -*- coding: utf-8 -*-

import socket
from copy import deepcopy
from flask_script import Command
from app.main import app
from app.models import *
from app.lib.notice import Notice
from app.account.user import get_user_auth, user_filter, set_user


"""
巡检mysql表:
        user
"""


class SyncUserInfo(Command):
    @classmethod
    def run(cls):
        with app.app_context():
            try:
                begin = datetime.now()
                user_list = User.get_by(show='login_name')
                for user in user_list:
                    try:
                        new_info = get_user_auth(user['login_name'])
                        new_info.pop('login_name')
                        new_info.pop('source')
                        new_info.pop('home_dir')
                        new_info.pop('shell')
                        new_info.pop('enable')
                        User.update(dict(login_name=user['login_name']), new_info)
                        user_info = User.get_by(login_name=user['login_name'], first=True)
                        user_filter(set_user(deepcopy(user_info)))
                        app.logger.info(u'同步账号{0} 成功'.format(user['login_name']))
                    except Exception as e:
                        app.logger.warn(u'同步账号{0} 失败，{1}'.format(user['login_name'], str(e)))

                app.logger.info(u'完成执行 user和hr系统同步，耗时：{0}'.format(datetime.now() - begin))

                message = u""" Jumper Job 执行成功
        执行机器: {0}
        Job名称：SyncUserInfo(User表企业系统信息同步)
        日志目录: /data/applogs/jumper-web/logs/app.log""".format(socket.gethostname())
                Notice(message, app.config['JOB_ADMIN'])
            except Exception as e:
                message = u""" Jumper Job 任务失败
        执行机器: {0}
        Job名称：SyncUserInfo(User表企业系统信息同步)
        日志目录: /data/applogs/jumper-web/logs/app.log
        失败原因: {1}""".format(socket.gethostname(), str(e))
                Notice(message, app.config['JOB_ADMIN'])
