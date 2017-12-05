# -*- coding:utf-8 -*-

import uuid
from datetime import datetime

from app.models import User
from app.account.user import get_user_info
from app.lib.http_client import http_client
from app.lib.app_redis import Rds
from app.lib.view_decorator import ViewDecorator


# web端登陆: redis一次性密码查询接口
@ViewDecorator('/web/redis_password', methods=['POST'])
def onetime_password(data):
    return Rds.router().onetime_password(data['post']['password'])


# web端登陆: 生成一次性code，供前端调用
@ViewDecorator('/web/code', methods=['POST'])
def onetime_token(data):
    _uuid = uuid.uuid4()
    user_info = dict(
        user_name=data['post']['user_name'],
        uuid=_uuid,
        host_name=data['post'].get('host_name'),
        origin=data['post']['origin'],
        register_time=datetime.now()
    )
    if Rds.router().set_token(user_info):
        return {'uuid': str(_uuid)}


# ttt关注的应用, 须登录SSO
@ViewDecorator('/mark/my', methods=['GET'])
def my_mark(data):
    user_info = get_user_info()
    url = u"http://ttt.dp/api/mark?user_name={0}"
    result = http_client(url.format(user_info['login_name']), method='get').json()
    return result
