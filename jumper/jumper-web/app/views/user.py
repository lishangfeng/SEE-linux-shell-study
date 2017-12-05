# -*- coding:utf-8 -*-

import time
from copy import deepcopy
from flask import redirect, session, g
from flask import current_app as app
from datetime import timedelta, datetime

from app.models import *
from app.lib.user import get_top_user
from app.lib.notice import Notice
from app.lib.falcon import Falcon
from app.lib.restful import RestfulGet
from app.account.user import get_user_info
from app.account.user import get_user_auth, user_filter, get_user, set_user
from app.lib.app_redis import Rds
from app.nss.nss_cache import NssCache
from app.lib.error_define import res
from app.account.password import Password
from app.lib.error_define import PermissionError
from app.lib.view_decorator import ViewDecorator


# 用户注册
@ViewDecorator('/user', methods=['POST'])
def user_add(data):
    user_info = data['post']
    # 修改时间将来时, 作为重置密码后的标志
    user_info['password_mtime'] = datetime.now() + timedelta(days=300)
    user_info.update(get_user_auth(user_info.pop('user_name')))
    # 初始化密码
    password = Password.random_password()
    password_sha1, salt = Password.get_password(password=password)
    user_info.update(dict(password=password_sha1, salt=salt))
    # 写数据库
    user_info = User.get_by_id(User.insert(**user_info))
    # 更新gid
    User.update(dict(uid=user_info['uid']), dict(gid=user_info['uid']))
    # 开始更新缓存
    user_info = get_user(login_name=user_info['login_name'])
    NssCache(user_list=[user_info]).start()
    # 发送消息给注册用户
    message = u"""Hi 您的跳板机账号申请成功, 请及时修改密码!
        登陆账号: {0}
        初始密码: {1}
使用指南: """.format(user_info['login_name'], password)
    message += app.config['WIKI']
    Notice(message, user_info['email'])
    return user_filter(deepcopy(user_info))


# 用户删除
@ViewDecorator('/user/<int:id>', methods=['DELETE'])
def user_delete(data):
    Auth.delete(role='user', role_id=data['get']['id'])
    Sudo.delete(role='user', role_name=data['user_info']['login_name'])
    Mapper.query.filter_by(uid=data['get']['id']).delete()
    User.delete(uid=data['get']['id'])
    Rds.router().hdel('nss_cache_user', data['user_info']['login_name'])
    Rds.router().del_user(data['user_info']['login_name'])


# 批量删除用户
@ViewDecorator('/user', methods=['DELETE'])
def bulk_del_user(data):
    name_list = []
    for uid in data['post']['user_list']:
        user_info = User.get_by_id(uid)
        if user_info:
            Auth.delete(role='user', role_id=uid)
            Sudo.delete(role='user', role_name=user_info['login_name'])
            Mapper.query.filter_by(uid=uid).delete()
            User.delete(uid=uid)
            Rds.router().hdel('nss_cache_user', user_info['login_name'])
            Rds.router().del_user(user_info['login_name'])
            name_list.append(user_info['login_name'])
    else:
        app.logger.info(u'{0} 删除用户：{1}'.format(session.get('CAS_USERNAME', 'None'), name_list))


# 用户信息和企业系统同步
@ViewDecorator('/user/sync', methods=['PUT'])
def sync_user(data):
    # 支持token 解锁账号和前端个人解锁账号
    if g.get('token'):
        pass
    elif get_user_info().get('role') in app.config['ADMIN_ROLE']:
        pass
    elif session.get('CAS_USERNAME') != data['post']['user_name']:
        raise PermissionError(u'Hi 您没有权限操作')
    
    user_name = data['post']['user_name']
    new_info = get_user_auth(user_name)
    new_info.pop('login_name')
    new_info.pop('source')
    new_info.pop('home_dir')
    new_info.pop('shell')
    new_info.pop('enable')
    
    User.update(dict(login_name=user_name), new_info)
    user_info = User.get_by(login_name=user_name, first=True)
    return user_filter(set_user(deepcopy(user_info)))


# 解除用户登陆锁定
@ViewDecorator('/user/unlocking', methods=['PUT'])
def unlocking_user(data):
    # 支持token 解锁账号和前端个人解锁账号
    user_name = ''
    if g.get('token'):
        user_name = 'workflow'
    elif get_user_info().get('role') in app.config['ADMIN_ROLE']:
        user_name = session.get('CAS_USERNAME')
    elif session.get('CAS_USERNAME') != data['post']['user_name']:
        raise PermissionError(u'Hi 您没有权限操作')

    app.logger.info(u'{0} 解除用户登录锁定'.format(user_name))
    return Rds.router().unlock_user(data['post']['user_name'])


# 用户修改
@ViewDecorator('/user/<int:id>', methods=['PUT'])
def user_update(data):
    User.update(dict(uid=data['get']['id']), data['post'])
    user_info = User.get_by_id(data['get']['id'])
    return user_filter(set_user(deepcopy(user_info)))


# 用户修改 (仅web端开放)
@ViewDecorator('/user/web/<int:id>', methods=['PUT'])
def web_user_update(data):
    User.update(dict(uid=data['get']['id']), data['post'])
    user_info = User.get_by_id(data['get']['id'])
    return user_filter(deepcopy(user_info))


# 修改uid
@ViewDecorator('/user/update/<string:user>', methods=['PUT'])
def user_update_uid(data):
    new_uid = dict(uid=data['post']['uid'], gid=data['post']['uid'])
    
    # update User
    old_uid = User.get_by(first=True, login_name=data['get']['user'])['uid']
    User.update(dict(login_name=data['get']['user']), new_uid)
    
    # update Mapper
    new_uid = dict(uid=data['post']['uid'])
    Mapper.update(dict(uid=old_uid), new_uid)
    
    # update Auth
    new_role_id = dict(role_id=data['post']['uid'])
    Auth.update(dict(role_id=old_uid, role='user'), new_role_id)
    return '{0} ok'.format(data['get']['user'])


# 用户重置密码
@ViewDecorator('/user/reset/password', methods=['POST'])
def user_reset_password(data):
    user_info = data['user_info']

    # 支持token重置密码和前端个人账号重置密码
    if g.get('token'):
        pass
    elif get_user_info().get('role') in app.config['ADMIN_ROLE']:
        pass
    elif session.get('CAS_USERNAME') != user_info['login_name']:
        raise PermissionError(u'Hi 您没有权限操作')

    password = Password.random_password()
    password_sha1, salt = Password.get_password(password=password)
    # 修改时间将来时, 作为重置密码后的标志
    password_mtime = datetime.now() + timedelta(days=300)
    
    # 保留过去密码
    old_password_dict = user_info.get('old_password_dict')
    deep_password = deepcopy(old_password_dict)
    if deep_password.get("password", None) is None:
        deep_password['password'] = ["", "", ""]
    deep_password['password'].pop()
    deep_password['password'].insert(0, password_sha1)
    
    uid_ = dict(uid=user_info['uid'])
    data_ = dict(password=password_sha1, salt=salt, password_mtime=password_mtime, old_password_dict=deep_password)
    User.update(uid_, data_)
    message = u'''Hi 您的跳板机重置密码成功: {0} 请及时修改.
使用指南: ''' + app.config['WIKI']
    Notice(message.format(password), user_info['email'])
    user_info = User.get_by_id(user_info['uid'])
    return user_filter(set_user(user_info))


# 用户查询
@ViewDecorator('/user', methods=['GET'])
def user_get(data):
    user_list = RestfulGet(User, data['get']).result
    [user_filter(user_info) for user_info in user_list['objects']]
    return user_list


# web端用户查询
@ViewDecorator('/web/user', methods=['GET'])
def get_web_user(data):
    user_list = RestfulGet(User, data['get']).result
    for user_info in user_list['objects']:
        lock_times = Rds.router().lock_times(user_info['login_name'])
        if lock_times:
            user_info['lock_times'] = int(lock_times)
        else:
            user_info['lock_times'] = 0
        user_filter(user_info)
    return user_list


# web端用户查询
@ViewDecorator('/user/group', methods=['GET'])
def user_group(data):
    uid = data['get']['uid']
    group_list = []
    [group_list.append(i['group_name']) for i in Mapper.get_by(uid=uid)]
    return group_list


# web端用户查询
@ViewDecorator('/user/relate/<int:uid>', methods=['GET'])
def user_relate(data):
    result = dict()
    uid = data['get']['uid']
    group_list = Mapper.get_by(uid=uid)
    
    # group information
    result['group'] = []
    for i in group_list:
        temp = {}
        temp['gid'] = i['gid']
        temp['group_name'] = i['group_name']
        if i['group_name'].startswith('sudo_sankuai'):
            temp['group_type'] = u'sudo sankuai组'
        else:
            temp['group_type'] = u'登录授权组'
        result['group'].append(temp)
    
    # auth information
    result['auth'] = []
    user_auth = Auth.get_by(role='user', role_id=uid)
    for i in user_auth:
        temp = {}
        if i['label'] in ['corp', 'owt', 'pdl', 'srv', 'cluster']:
            temp['location'] = u'北京'
            temp['label'] = i['label']
        elif i['label'] == 'dp_project':
            temp['location'] = u'上海'
            temp['label'] = u'应用'
        elif i['label'] == 'dp_host':
            temp['location'] = u'上海'
            temp['label'] = u'单机授权'
        elif i['label'] == 'host_fqdn':
            temp['location'] = u'北京'
            temp['label'] = u'单机授权'
        if not i['life_cycle']:
            temp['expire'] = u'永久有效'
        elif i['life_cycle'] and i['life_cycle'] <= datetime.now():
            temp['expire'] = i['life_cycle']
        else:
            continue
        temp['label_key'] = i['label_key']
        result['auth'].append(temp)
        
    for group in group_list:
        user_group_auth = Auth.get_by(role='group', role_id=group['gid'])
        for i in user_group_auth:
            temp = {}
            if i['label'] in ['corp', 'owt', 'pdl', 'srv', 'cluster']:
                temp['location'] = u'北京'
                temp['label'] = i['label']
            elif i['label'] == 'dp_project':
                temp['location'] = u'上海'
                temp['label'] = u'应用'
            elif i['label'] == 'dp_host':
                temp['location'] = u'上海'
                temp['label'] = u'单机授权'
            elif i['label'] == 'host_fqdn':
                temp['location'] = u'北京'
                temp['label'] = u'单机授权'
            if not i['life_cycle']:
                temp['expire'] = u'永久有效'
            elif i['life_cycle'] and i['life_cycle'] <= datetime.now():
                temp['expire'] = i['life_cycle']
            else:
                continue
            temp['label_key'] = i['label_key']
            result['auth'].append(temp)
    
    # sudo information
    result['sudo'] = []
    user_name = User.get_by_id(uid)['login_name']
    user_sudo = Sudo.get_by(role='user', role_name=user_name)
    for i in user_sudo:
        temp = {}
        if i['label'] in ['corp', 'owt', 'pdl', 'srv', 'cluster']:
            temp['location'] = u'北京'
            temp['label'] = i['label']
        elif i['label'] == 'dp_project':
            temp['location'] = u'上海'
            temp['label'] = u'应用'
        elif i['label'] == 'dp_host':
            temp['location'] = u'上海'
            temp['label'] = u'单机授权'
        elif i['label'] == 'host_fqdn':
            temp['location'] = u'北京'
            temp['label'] = u'单机授权'
        if not i['life_cycle']:
            temp['expire'] = u'永久有效'
        elif i['life_cycle'] and i['life_cycle'] <= datetime.now():
            temp['expire'] = i['life_cycle']
        else:
            continue
        temp['label_key'] = i['label_key']

        content = "{0}  {1}=({2}) {3}: {4}\n"
        temp['content'] = content.format(i['role_name'], i['hosts'], i['users'], i['password_option'], i['commands'])
        result['sudo'].append(temp)

    for group in group_list:
        user_group_auth = Sudo.get_by(role='group', role_name=group['group_name'])
        for i in user_group_auth:
            temp = {}
            if i['label'] in ['corp', 'owt', 'pdl', 'srv', 'cluster']:
                temp['location'] = u'北京'
                temp['label'] = i['label']
            elif i['label'] == 'dp_project':
                temp['location'] = u'上海'
                temp['label'] = u'应用'
            elif i['label'] == 'dp_host':
                temp['location'] = u'上海'
                temp['label'] = u'单机授权'
            elif i['label'] == 'host_fqdn':
                temp['location'] = u'北京'
                temp['label'] = u'单机授权'
            if not i['life_cycle']:
                temp['expire'] = u'永久有效'
            elif i['life_cycle'] and i['life_cycle'] <= datetime.now():
                temp['expire'] = i['life_cycle']
            else:
                continue
            temp['label_key'] = i['label_key']
            content = "%{0}  {1}=({2}) {3}: {4}\n"
            temp['content'] = content.format(i['role_name'], i['hosts'], i['users'], i['password_option'],
                                             i['commands'])
            result['sudo'].append(temp)
    
    return result


# 根据uid查询用户
@ViewDecorator('/user/<int:id>', methods=['GET'])
def user_get_by_id(data):
    result = User.get_by_id(data['get']['id'])
    return user_filter(result) if result else None


# sso 跳转页
@app.route('/api/user/register')
def user_register():
    user_info = get_user_info()
    if user_info.get('uid'):
        User.update(query=dict(login_name=user_info['login_name']), data=dict(login_time=datetime.now()))
    else:
        User.insert(**user_info)
    return redirect('/')


# 获取个人信息
@app.route('/api/user/my')
def user_my():
    return res(user_filter(get_user_info()))


# 首页展示
@ViewDecorator('/user/top', methods=['GET'])
def user_top(data):
    user_num = User.query.count()
    host_num = Host.query.count()
    records = LoginHistory.query.order_by(-LoginHistory.login_time).limit(data['get'].get('limit', 10))  # 最近10条登录记录
    top_records = [{'user_name': record.user_name, 'host_name': record.host_name, 'login_time': record.login_time}
                   for record in records]
    top_users = get_top_user(data['get'].get('interval', 7))  # 周top10用户
    values = Falcon.get_chart_data(data['get'].get('duration', 15))  # falcon 两周历史数据
    result = dict(
            user_num=user_num,
            host_num=host_num,
            top_user=top_users[::-1],
            top_record=top_records,
            chart_data=values
    )
    return result
