# -*- coding: utf-8 -*-

from app.lib.monitor import Monitor
from app.lib.utlis import get_session
from app.lib.view_decorator import ViewDecorator


@ViewDecorator('/monitor', methods=['GET'], args=False)
def jumper_monitor():
    """ falcon监控数据上报 """
    return Monitor().process()


@ViewDecorator('/user/session', methods=['GET'])
def user_session(data):
    """ 当前用户session具体情况 """
    return get_session(data.get('user_name', None))
