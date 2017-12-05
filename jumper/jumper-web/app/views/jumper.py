# -*- coding:utf-8 -*-

import re
import copy
from datetime import datetime

from app.main import app
from app.models import User, Host, Session
from app.models import LoginHistory, CommandHistory
from app.pam.session import UUID, SessionFilter
from app.lib.restful import RestfulGet
from app.account.user import get_user, set_user
from app.lib.app_redis import Rds
from app.account.password import Password
from app.lib.view_decorator import ViewDecorator


@ViewDecorator('/jumper/clean', methods=['POST'])
def clean_up(data):
    _data = data['post']
    uuid = _data['uuid']
    source = _data['source']
    username = _data['username']

    # 清理会话
    UUID.delete(source=source, uuid=uuid)
    Session.update(dict(uuid=uuid), dict(logout_time=datetime.now()))

    # 清理heartbeat信息
    Rds.router().hdel('heartbeat', '{0}:{1}'.format(username, uuid))


@ViewDecorator('/jumper/heartbeat', methods=['GET'])
def heartbeat_get(data):
    all = Rds.router().hgetall('heartbeat')
    return all


@ViewDecorator('/jumper/heartbeat', methods=['POST'])
def heartbeat(data):
    _data = data['post']

    if not _data['data']:
        Rds.router().hdel('heartbeat', '{0}:{1}'.format(_data['user_name'], _data['uuid']))
    else:
        Rds.router().hset('heartbeat', '{0}:{1}'.format(_data['user_name'], _data['uuid']), _data['data'])


# 用户行为: 伪终端获取用户数据, 原始db数据
@ViewDecorator('/jumper/user', methods=['GET'])
def jumper_user_get(data):
    # 账号信息优先取自mysql， mysql挂去redis取
    # redis挂了自动降级账号锁定功能， 两个都挂了就没意思了
    try:
        objects = RestfulGet(User, data['get']).result.get('objects')
    except Exception as e:
        app.logger.error(u'db出现故障, 从redis中获取账号信息: {0}'.format(str(e)))
        if data['get'].get('login_name'):
            objects = [get_user(login_name=data['get']['login_name'])]
        else:
            return
    if objects:
        user_info = objects[0]
        try:
            lock_times = Rds.router().lock_times(user_info['login_name'])
        except Exception as e:
            app.logger.error(u'redis请求lock_times出错, 自动降级忽略检查密码错误次数： {0}'.format(str(e)))
            lock_times = 0
        if lock_times:
            user_info['lock_times'] = int(lock_times)
        else:
            user_info['lock_times'] = 0
        return user_info


# 用户行为: 修改用户信息, 登陆时间等碎片信息
@ViewDecorator('/jumper/user', methods=['POST'])
def jumper_update_user(data):
    post_data = data['post']['data']
    query_string = data['post']['query_string']
    User.update(query_string, post_data)


# 用户行为: 伪终端修改用户密码
@ViewDecorator('/jumper/user', methods=['PUT'])
def jumper_update_password(data):
    post_data = data['post']['data']
    if not post_data.get('password'):
        """ 用户未提交数据 放弃更新密码 """
        return
    query_string = data['post']['query_string']
    password_sha1, salt = Password.get_password(password=post_data.get('password'))
    old_password_dict = User.query.filter_by(**query_string).first().old_password_dict
    deep_password = copy.deepcopy(old_password_dict)
    if deep_password.get("password", None) is None:
        deep_password['password'] = ["", "", ""]
    deep_password['password'].pop()
    deep_password['password'].insert(0, password_sha1)
    post_data.update(dict(password=password_sha1, salt=salt, password_mtime=datetime.now(),
                          old_password_dict=deep_password))
    User.update(query_string, post_data)
    result = User.get_by(first=True, **query_string)
    set_user(result)
    return result if result else u"用户不存在, 忽略更新."


# 登陆行为: 用户密码试错锁定
@ViewDecorator('/jumper/locked', methods=['POST'])
def lock_user(data):
    login_name = data['post']['login_name']
    lock_user_ttl = data['post']['lock_user_ttl']
    return Rds.router().lock_user(login_name, lock_user_ttl)


# 登陆行为: 解除用户登陆锁定
@ViewDecorator('/jumper/unlock', methods=['POST'])
def unlock_user(data):
    return Rds.router().unlock_user(data['post']['login_name'])


# 登录历史: 添加登陆历史
@ViewDecorator('/jumper/login_history', methods=['POST'])
def login_history_add(data):
    host_name = Host.get_by(host_name=data['post']['host_name'], first=True, show='host_name,host_ip')
    if not host_name:
        host_name = Host.get_by(host_ip=data['post']['host_name'], first=True, show='host_name,host_ip')
        if not host_name:
            host_name = Host.get_by(host_fqdn=data['post']['host_name'], first=True, show='host_name,host_ip')

    if host_name:
        new_host = dict(host_name=host_name['host_name'], host_ip=host_name['host_ip'])
        data['post'].update(new_host)
    return LoginHistory.get_by_id(LoginHistory.insert(**data['post']))


# 登录历史: 记录登出时间
@ViewDecorator('/jumper/login_history', methods=['PUT'])
def login_history_update(data):
    query_string = data['post']['query_string']
    LoginHistory.update(query_string, data['post']['data'])


# 登录历史: 最近30条不重复的登陆记录
@ViewDecorator('/jumper/login_history', methods=['GET'])
def login_history_get(data):
    result = list()
    unique = set()
    data = LoginHistory.query.filter_by(user_uid=data['get']['user_uid']).order_by(-LoginHistory.id).limit(300)
    for i in data:
        if len(unique) >= 30:
            break
        if i.host_name not in unique:
            unique.add(i.host_name)
            result.append(i.to_dict())
    return result


# 用户session: 插入
@ViewDecorator('/jumper/uuid', methods=['POST'])
def jumper_uuid_set(data):
    if UUID.set(source=data['post']['source'], info=data['post']['connection_info']):
        SessionFilter(source=data['post']['source'], info=data['post']['connection_info'])
        return True
    else:
        return None


# 用户session: 检查会话过期
@ViewDecorator('/jumper/uuid', methods=['GET'])
def jumper_uuid_get(data):
    return UUID.get(source=data['get']['source'], uuid=data['get']['uuid'])


# 用户session: 伪终端退出清理会话
@ViewDecorator('/jumper/uuid', methods=['DELETE'])
def jumper_uuid_del(data):
    UUID.delete(source=data['post']['source'], uuid=data['post']['uuid'])
    SessionFilter(source=data['post']['source'], info=data['post']['uuid'])


# 历史命令: 记录伪终端历史命令
@ViewDecorator('/jumper/history', methods=['POST'])
def jumper_history_add(data):
    login_name = data['post']['login_name']
    user_info = get_user(login_name=login_name)
    if user_info:
        return Rds.router(user_info['source']).set_history(data['post'])


# 历史命令: 伪终端加载历史命令
@ViewDecorator('/jumper/history', methods=['GET'])
def jumper_history_get(data):
    login_name = data['get']['login_name']
    user_info = get_user(login_name=login_name)
    if user_info:
        return Rds.router(user_info['source']).get_history(data['get']['login_name'])


# 后端机器命令
@ViewDecorator('/jumper/command', methods=['POST'])
def add_command(data):
    _data = data['post']
    cmd = _data.pop('command')
    try:
        if isinstance(cmd[0][1], float):    # 过渡阶段
            return

        # 用户终端下输入的主机名可能是ip, host_name,或者host_fqdn, 查询到了主机信息就修正，未查询到就默认塞host_name
        host = data['post']['host_name']
        host_name = Host.get_by(host_name=host, first=True, show='host_name,host_ip')
        if not host_name:
            host_name = Host.get_by(host_ip=host, first=True, show='host_name,host_ip')
            if not host_name:
                host_name = Host.get_by(host_fqdn=host, first=True, show='host_name,host_ip')

        for i in cmd:
            danger = 0
            if len(i) == 2:
                command, exec_time = i
            else:
                command, exec_time, danger = i
            _data.update(dict(command=command, exec_time=exec_time, danger=danger))
            if host_name:
                new_host = dict(host_name=host_name['host_name'], host_ip=host_name['host_ip'])
                _data.update(new_host)
            CommandHistory.insert(**_data)
    except Exception as e:
        app.logger.warning(u'插入历史命令到db出错:{0}'.format(str(e)))
        pass


# 权限提醒: 删除权限提示
@ViewDecorator('/jumper/permission', methods=['DELETE'])
def permission_del(data):
    return Rds.router().delete(data['post']['key'])


# 权限提醒: 获取权限提醒
@ViewDecorator('/jumper/permission', methods=['GET'])
def permission_get(data):
    return Rds.router().get(data['get']['key'])


# cmdb:伪终端查询mt某节点下机器
@ViewDecorator('/jumper/mt_cmdb', methods=['POST'])
def jumper_host_corp(data):
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', data['post']['host']):
        result = Host.query.filter_by(host_ip=data['post']['host']).first()
    else:
        result = Host.query.filter_by(host_name=data['post']['host']).first()
    return result.corp if result else ''
