# -*- coding:utf-8 -*-

import json

from app.main import app
from app.models import *
from app.lib.utlis import date_handler
from app.lib.restful import RestfulGet
from app.lib.view_decorator import ViewDecorator


@ViewDecorator('/auth', methods=['GET'])
def auth_get(data):
    return RestfulGet(Auth, data['get']).result


@ViewDecorator('/auth/<int:id>', methods=['GET'])
def auth_get_by_id(data):
    return Auth.get_by(id=data['get']['id'])


@ViewDecorator('/auth', methods=['POST'])
def auth_add(data):
    app.logger.info(u'新增权限,Role:{0}, Role_Id:{1}, Label:{2}, Label_key:{3}'.format(
        data['post']['role'],
        data['post']['role_id'],
        data['post']['label'],
        data['post']['label_key'])
    )
    return Auth.get_by_id(Auth.insert(**data['post']))


@ViewDecorator('/auth/<int:id>', methods=['PUT'])
def auth_update(data):
    Auth.update(dict(id=data['get']['id']), data['post'])
    return Auth.get_by_id(data['get']['id'])


@ViewDecorator('/auth/<int:id>', methods=['DELETE'])
def auth_delete(data):
    auth_info = Auth.get_by_id(data['get']['id'])
    app.logger.info(u'删除权限: {0}'.format(json.dumps(auth_info, default=date_handler, ensure_ascii=False)))
    Auth.delete(id=data['get']['id'])


# 某个用户有ssh权限的北京侧机器
@ViewDecorator('/auth/user/<int:uid>', methods=['GET'])
def web_auth(data):
    groups = Mapper.query.filter_by(uid=data['get']['uid']).all()
    group_list = [group.gid for group in groups]

    auths = Auth.query.filter_by(role='user', role_id=data['get']['uid']).all()
    auth_list = [auth.to_dict() for auth in auths]

    inherit_auths = Auth.query.filter_by(role='group').filter(Auth.role_id.in_(group_list)).all() \
                                                                                    if len(group_list) != 0 else []
    inherit_auth_list = [auth.to_dict() for auth in inherit_auths]

    result = dict(
        inherit=inherit_auth_list,
        un_inherit=auth_list
    )
    return result
