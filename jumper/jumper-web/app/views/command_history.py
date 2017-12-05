# -*- coding: utf-8 -*-

from app.models import CommandHistory
from app.lib.restful import RestfulGet
from app.lib.view_decorator import ViewDecorator


# 查询后端机器历史命令
@ViewDecorator('/command', methods=['GET'])
def command_history_get(data):
    return RestfulGet(CommandHistory, data['get']).result
