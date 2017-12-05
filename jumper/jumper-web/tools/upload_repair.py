# -*- coding: utf-8 -*-

from flask_script import Command
from app.main import app
from app.lib.app_redis import Rds


def upload():
    """
        上传repair-jumper脚本
    """
    with open('tools/repair-jumper.sh') as fd:
        my_script = fd.read()
        Rds.router().set('repair_jumper', my_script)
        app.logger.info(u'上传repair-jumper脚本成功!')


class Upload(Command):
    @classmethod
    def run(cls):
        with app.app_context():
            upload()
