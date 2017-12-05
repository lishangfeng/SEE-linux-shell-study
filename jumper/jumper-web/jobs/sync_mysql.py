# -*- coding: utf-8 -*-

import socket
from flask_script import Command
from app.main import app
from app.models import *
from app.lib.app_redis import Rds
from app.lib.notice import Notice


"""
巡检mysql表:
        session
        login_history
"""


def session():
    count = 0
    keys = [k for k in Rds.router().scan_iter(match='login_uuid_{0}'.format('*'), count=500)]
    login_uuid = set([i[11:] for i in keys])
    trash = Session.get_by(logout_time=None)

    for sess in trash:
        if sess['uuid'] not in login_uuid:
            count += 1
            app.logger.info(u'关闭登出时间 session , {0}'.format(sess))
            Session.update(query=sess, data=dict(logout_time=datetime.now()))
    return u'关闭session登出时间数: {0}'.format(count)


def login_history():
    count = 0
    keys = [k for k in Rds.router().scan_iter(match='login_uuid_{0}'.format('*'), count=500)]
    login_uuid = set([i[11:] for i in keys])
    trash = LoginHistory.get_by(logout_time=None)

    for sess in trash:
        if sess['session_uuid'] not in login_uuid:
            count += 1
            app.logger.info(u'关闭登出时间 login_history , {0}'.format(sess))
            LoginHistory.update(query=sess, data={'logout_time': datetime.now()})
    return u'关闭登录历史登出时间数: {0}'.format(count)


class SyncMysql(Command):
    @classmethod
    def run(cls):
        with app.app_context():
            try:
                begin = datetime.now()
                # session
                st = datetime.now()
                app.logger.info(u'开始执行 session 检查')
                _session = session()
                app.logger.info(u'完成执行 session 检查，耗时：{0}'.format(datetime.now() - st))

                # login_history
                st = datetime.now()
                app.logger.info(u'开始执行 login_history 检查')
                _login_history = login_history()
                app.logger.info(u'完成执行 login_history 检查，耗时：{0}'.format(datetime.now() - st))

                app.logger.info(u'此次job执行总耗时:{0}'.format(datetime.now() - begin))
                app.logger.info('*' * 40)
                message = u""" Jumper Job 执行成功
        执行机器: {0}
        Job名称：SyncMysql(session和login_history表)
        本次同步列表:
            session:{1}
            login_history:{2}
        日志目录: /data/applogs/jumper-web/logs/app.log""".format(socket.gethostname(),
                                                              _session,
                                                              _login_history)
                Notice(message, app.config['JOB_ADMIN'])
            except Exception as e:
                message = u""" Jumper Job 任务失败
        执行机器: {0}
        Job名称：SyncMysql(session和login_history表)
        日志目录: /data/applogs/jumper-web/logs/app.log
        失败原因: {1}""".format(socket.gethostname(), str(e))
                Notice(message, app.config['JOB_ADMIN'])
