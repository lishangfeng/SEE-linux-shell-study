# -*- coding: utf-8 -*-

from lion import Lion
from app.lib.view_decorator import ViewDecorator
from flask import current_app as app


@ViewDecorator('/lion', methods=['GET'])
def lion_update(data):
    if app.config.get('lion_update_time'):
        return app.config.get('lion_update_time')
    else:
        return 'no lion'


class NewLion(object):
    def __init__(self):
        self.lion = Lion(flask=True)

    def init_app(self, app):
        self.lion.init_app(app.config['APP_NAME'], app.config)

extension = NewLion()
