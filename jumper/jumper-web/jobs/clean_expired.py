# -*- coding: utf-8 -*-

import socket
from flask_script import Command
from app.main import app
from app.models import *
from app.lib.notice import Notice
from app.extensions.sqlalchemy import extension as db


"""
巡检mysql表:
        auth
        sudo
"""


def auth():
    count = 0
    auths = Auth.query.filter(Auth.life_cycle < datetime.now()).all()
    for x in auths:
        count += 1
        app.logger.info(u'删除过期 auth(授权信息) : {0}'.format(x.to_dict()))
        Auth.query.filter_by(id=x.id).delete()
    db.session.commit()
    return u'删除过期auth条目数:{0}'.format(count)


def sudo():
    count = 0
    sudoers = Sudo.query.filter(Sudo.life_cycle < datetime.now()).all()
    for x in sudoers:
        count += 1
        app.logger.info(u'删除过期 sudo : {0}'.format(x.to_dict()))
        Sudo.query.filter_by(id=x.id).delete()
    db.session.commit()
    return u'删除过期sudo条目数:{0}'.format(count)


class CleanExpired(Command):
    @classmethod
    def run(cls):
        with app.app_context():
            try:
                begin = datetime.now()
                # auth
                st = datetime.now()
                app.logger.info(u'开始执行 auth 检查')
                _auth = auth()
                app.logger.info(u'完成执行 auth 检查，耗时：{0}'.format(datetime.now() - st))

                # sudo
                st = datetime.now()
                app.logger.info(u'开始执行 sudo 检查')
                _sudo = sudo()
                app.logger.info(u'完成执行 sudo 检查，耗时：{0}'.format(datetime.now() - st))

                app.logger.info(u'此次job执行总耗时:{0}'.format(datetime.now() - begin))
                app.logger.info('*' * 40)
                message = u""" Jumper Job 执行成功
        执行机器: {0}
        Job名称：ExpiredData(过期授权和sudo)
        本次同步列表:
            auth:{1}
            sudo:{2}
        日志目录: /data/applogs/jumper-web/logs/app.log""".format(socket.gethostname(),
                                                                _auth,
                                                                _sudo)
                Notice(message, app.config['JOB_ADMIN'])
            except Exception as e:
                message = u""" Jumper Job 任务失败
        执行机器: {0}
        Job名称：ExpiredData(过期授权和sudo)
        日志目录: /data/applogs/jumper-web/logs/app.log
        失败原因: {1}""".format(socket.gethostname(), str(e))
                Notice(message, app.config['JOB_ADMIN'])
