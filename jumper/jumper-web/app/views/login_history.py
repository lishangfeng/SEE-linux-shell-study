# -*- coding: utf-8 -*-

from app.models import LoginHistory
from app.lib.restful import RestfulGet
from app.lib.view_decorator import ViewDecorator


@ViewDecorator('/login', methods=['GET'])
def login_get(data):
    return RestfulGet(LoginHistory, data['get']).result
