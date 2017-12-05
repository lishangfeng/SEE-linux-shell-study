# -*- coding: utf-8 -*-

from app.models import LoginHistory
from app.lib.restful import RestfulGet
from app.lib.history import history_filter
from app.lib.view_decorator import ViewDecorator


# 用户登录历史: 某用户的主机登录记录
@ViewDecorator('/history', methods=['GET'])
def get_host_history(data):
    _data = data['get']
    _data['order_by'] = u'login_time'
    return RestfulGet(LoginHistory, _data).result


# 主机登录历史: 某主机的用户登录记录
@ViewDecorator('/history', methods=['POST'])
def get_user_history(data):
    result = []
    for host in data['post']['host_list']:
        host_query = LoginHistory.query.filter_by(host_name=host)
        from_query = host_query.filter(LoginHistory.login_time >= data['post']['start_time'])
        to_query = from_query.filter(LoginHistory.login_time <= data['post']['end_time'])
        users = to_query.all()
        user_list = [history_filter(user.to_dict()) for user in users]
        result.append(dict(
            host=host,
            count=len(user_list),
            user_list=user_list
        ))
    return result
