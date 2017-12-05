# -*- coding: utf-8 -*-

from flask import current_app as app
from app.models import LoginHistory
from app.lib.app_redis import Rds


class Monitor:
    def __init__(self):
        self.result = dict()

    def process(self):
        self.count_session()
        self.backend_online()
        return self.result

    def count_session(self):
        """ 用户和session统计 """
        for s in app.config.get('REDIS_POOL'):
            if s not in ['readonly']:
                user_online, session_online = Rds.router(source=s).count_session()
                if s == 'default':
                    self.result['mt_user_online'] = user_online
                    self.result['mt_session_online'] = session_online
                else:
                    self.result['%s_user_online' % s] = user_online
                    self.result['%s_session_online' % s] = session_online

    def backend_online(self):
        all = Rds.router(readonly=True).hgetall('heartbeat')
        # all_user_online = len(all)
        backend_online = 0
        for i in all.values():
            for j in eval(i):
                if j.split('&')[1] != 'None':
                    backend_online += 1
        # count = LoginHistory.query.filter_by(logout_time=None).count()
        self.result['backend_online'] = backend_online

    def login_jumper_error(self):
        pass

    def login_backend_error(self):
        pass

    def login_backend_time(self):
        pass

    def command_count(self):
        pass
