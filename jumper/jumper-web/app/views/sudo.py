# -*- coding:utf-8 -*-

from app.models import *
from app.lib.restful import *
from app.sudo.sudoers import SudoInfo, AddSudo
from app.sudo.sudo_cache import SudoCache
from app.sudo.sudo_config import SudoConfig
from app.lib.view_decorator import ViewDecorator


# 北京sudo添加接口
@ViewDecorator('/sudo', methods=['POST'])
def sudo_add(data):
    _data = data['post']
    _log_fmt = u'新增sudo权限, Role:{0}, Role_name:{1}, Label:{2}, Label_key:{3}'
    app.logger.info(_log_fmt.format(_data['role'], _data['role_name'], _data['label'], _data['label_key']))
    ret = Sudo.get_by_id(Sudo.insert(**data['post']))
    SudoCache(ret).start()
    return ret


# 上海sudo添加接口, 内含个性化设置
@ViewDecorator('/sh/sudo', methods=['POST'])
def sh_sudo_add(data):
    ret = AddSudo(data).process()
    SudoCache(data['post'], corp='dianping').start()
    return ret


# 上海sudo添加接口, 内含个性化设置
@ViewDecorator('/sankuai/sudo', methods=['POST'])
def sankuai_sudo_add(data):
    ret = AddSudo(data).process(sankuai='sankuai')
    SudoCache(data['post'], corp='dianping').start()
    return ret


@ViewDecorator('/sudo/<int:id>', methods=['DELETE'])
def sudo_delete(data):
    _data = data['sudo_info']
    _log_fmt = u'删除sudo权限, Role:{0}, Role_name:{1}, Label:{2}, Label_key:{3}'
    app.logger.info(_log_fmt.format(_data['role'], _data['role_name'], _data['label'], _data['label_key']))
    Sudo.delete(id=data['get']['id'])
    SudoCache(data['sudo_info']).start()


@ViewDecorator('/sudo/<int:id>', methods=['PUT'])
def sudo_update(data):
    _log_fmt = u'更新sudo权限, Role:{0}, Role_name:{1}, Label:{2}, Label_key:{3}'
    Sudo.update(dict(id=data['get']['id']), data=data['post'])
    _data = Sudo.get_by_id(data['get']['id'])
    app.logger.info(_log_fmt.format(_data['role'], _data['role_name'], _data['label'], _data['label_key']))
    SudoCache(_data).start()
    return _data


@ViewDecorator('/sudo', methods=['GET'])
def sudo_get(data):
    return RestfulGet(Sudo, data['get']).result


@ViewDecorator('/sudoers', methods=['GET'])
def sudo_info(data):
    return SudoInfo(data).process()


@ViewDecorator('/sudo/config', methods=['GET'])
def sudo_config(data):
    return SudoConfig(data['host_info']).result


@ViewDecorator('/sudo/cache', methods=['GET'])
def sudo_cache(data):
    return SudoCache.fetch_cache(data['host_info'])


# 某个用户的所有sudo权限
@ViewDecorator('/sudo/<string:user_name>', methods=['GET'])
def web_sudo_get(data):
    groups = Mapper.query.filter_by(user_name=data['get']['user_name']).all()
    group_list = [group.group_name for group in groups]

    sudos = Sudo.query.filter_by(role_name=data['get']['user_name']).all()
    sudo_list = [sudo.to_dict() for sudo in sudos]

    inherit_sudos = []
    if len(group_list) != 0:
        inherit_sudos = Sudo.query.filter(Sudo.role.in_(['dp_group', 'group']), Sudo.role_name.in_(group_list)).all()
    inherit_sudo_list = [sudo.to_dict() for sudo in inherit_sudos]

    result = dict(
        inherit=inherit_sudo_list,
        un_inherit=sudo_list
    )
    return result
