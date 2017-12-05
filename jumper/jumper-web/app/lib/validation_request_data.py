# -*- coding: utf-8 -*-

import re

from flask import current_app as app
from app.models import *
from app.account.user import get_user
from app.host.host_cache import HostCache
from app.lib.error_define import SupportError
from app.lib.error_define import ValidationError
from app.lib.validation_rules import rules


class PreProcessorChain(object):
    """数据逻辑验证
    """
    @classmethod
    def process(cls, process_type, request_data):
        cls.get = request_data['get']
        cls.post = request_data['post']
        if process_type in cls.__dict__.keys():
            return cls.__dict__[process_type](cls)
        else:
            return False

    def auth_add(self):
        if self.post['role'] == 'user':
            if not User.get_by_id(self.post['role_id']):
                raise SupportError(u'该用户ID不存在, 无法授权: {0}'.format(self.post['role_id']))
        elif self.post['role'] == 'group':
            if not Group.get_by_id(self.post['role_id']):
                raise SupportError(u'该组ID不存在, 无法授权: {0}'.format(self.post['role_id']))
        if Auth.get_by(**self.post):
            raise SupportError(u'该数据已经存在, 无需重复添加!')

    def auth_delete(self):
        if not Auth.get_by_id(self.get['id']):
            raise SupportError(u'删除失败, id不存在: {0}'.format(self.get['id']))

    def auth_update(self):
        if not Auth.get_by_id(self.get['id']):
            raise SupportError(u'更新失败, id不存在: {0}'.format(self.get['id']))

    def group_add(self):
        if Group.get_by(group_name=self.post['group_name']):
            raise SupportError(u'该用户组已存在')
        elif User.get_by(login_name=self.post['group_name']):
            raise SupportError(u'该用户组已存在')
        if self.post.get('user_list'):
            user_list = list()
            for user_name in self.post['user_list']:
                user_info = get_user(login_name=user_name)
                if not user_info:
                    app.logger.warning(u'用户不存在: {0}'.format(user_name))
                    continue
                elif Mapper.get_by(group_name=self.post['group_name'], user_name=user_name):
                    app.logger.warning(u'用户组关系已存在: {0} - {1}'.format(self.post['group_name'], user_name))
                    continue
                user_list.append(user_info)
            return dict(user_list=user_list)

    def group_delete(self):
        group_info = Group.get_by(group_name=self.post['group_name'], first=True)
        if not group_info:
            raise SupportError(u'该用户组不存在:{0}'.format(self.post['group_name']))
        else:
            return dict(group_info=group_info)

    def group_update(self):
        user_list = list()
        group_info = Group.get_by(group_name=self.post['group_name'], first=True)
        if not group_info:
            raise SupportError(u'用户组不存在, 放弃添加!')
        for user_name in self.post['user_list']:
            user_info = get_user(login_name=user_name)
            if not user_info:
                app.logger.warning(u'用户不存在: {0}'.format(user_name))
                continue
            elif Mapper.get_by(gid=group_info['gid'], uid=user_info['uid']):
                app.logger.warning(u'用户组关系已存在: {0} - {1}'.format(group_info['group_name'], user_name))
                continue
            user_list.append(user_info)
        return dict(group_info=group_info, user_list=user_list)

    def group_members(self):
        group_name = self.get.get('group_name')
        user_list = list()
        group_list = list()
        if self.get.get('group_name'):
            if Group.query.filter_by(group_name=group_name).first():
                group_info = Mapper.query.filter_by(group_name=self.get.get('group_name')).all()
                if group_info:
                    for group in group_info:
                        group_list.append(group)
                    return dict(user_list=user_list, group_list=group_list)
                raise SupportError("Group Don't have members!")
            raise SupportError('Group Not Exist')

    def host_add(self):
        requests_data = self.post
        if Host.query.filter_by(host_name=requests_data['host_name']).first():
            raise SupportError(u'该主机host_name已经存在: {0}'.format(requests_data['host_name']))

    def host_delete(self):
        host_info = Host.query.get(self.get.get('id'))
        if not host_info:
            raise SupportError(u'id 不存在: {0}'.format(self.get.get('id')))
        else:
            return dict(host_info=host_info.to_dict())

    def host_update(self):
        if not Host.query.filter_by(id=self.get.get('id')):
            raise SupportError(u'id 不存在: {0}'.format(self.get.get('id')))

    def pam_password(self):
        try:
            user_info = User.get_by(first=True, login_name=self.get['user_name'])
        except Exception:   # db故障后从redis取
            app.logger.error(u'db故障，从redis取缓存账号：{0}'.format(self.get['user_name']))
            user_info = get_user(login_name=self.get['user_name'])
        if not user_info:
            app.logger.info(u'验证密码失败, 用户不存在:{0}'.format(self.get['user_name']))
            raise SupportError('User Not Exist')
        return dict(user_info=user_info)

    def pam_account(self):
        try:
            user_info = User.get_by(first=True, login_name=self.get['user_name'])
        except Exception:   # db故障后从redis取
            app.logger.error(u'db故障，从redis取缓存账号：{0}'.format(self.get['user_name']))
            user_info = get_user(login_name=self.get['user_name'])
            if user_info:
                user_info['db_error'] = True
        if not user_info:
            app.logger.info(u'验证账号授权失败, 用户不存在:{0}'.format(self.get['user_name']))
            raise SupportError('User Not Exist')
        return dict(user_info=user_info)

    def sudo_add(self):
        if self.post['role'] == 'user':
            if not User.query.filter_by(login_name=self.post['role_name']).first():
                raise SupportError(u'该用户不存在, 无法添加sudo授权: {0}'.format(self.post['role_name']))
        elif self.post['role'] == 'group':
            if not Group.query.filter_by(group_name=self.post['role_name']).first():
                raise SupportError(u'该组名不存在, 无法添加sudo授权: {0}'.format(self.post['role_name']))
        if Sudo.query.filter_by(**self.post).first():
            raise SupportError(u'组或用户已经存在同层级下sudo授权: {0}'.format(self.post['role_name']))

    def sh_sudo_add(self):
        if not User.query.filter_by(login_name=self.post['user_name']).first():
            raise SupportError(u'该用户不存在, 无法添加sudo授权: {0}'.format(self.post['user_name']))
        if not isinstance(self.post['data'], list):
            raise SupportError(u'data非正确数据类型'.format(self.post['data']))

    def sankuai_sudo_add(self):
        if not User.query.filter_by(login_name=self.post['user_name']).first():
            raise SupportError(u'该用户不存在, 无法添加sudo授权: {0}'.format(self.post['user_name']))
        if not isinstance(self.post['data'], list):
            raise SupportError(u'data非正确数据类型'.format(self.post['data']))

    def onetime_token(self):
        # raise SupportError(u'此功能暂时关闭～请知晓.'.format(self.post['user_name']))
        if not User.query.filter_by(login_name=self.post['user_name']).first():
            raise SupportError(u'用户[{0}]未申请Jumper账号,登录失败,如有需要请联系该应用SRE负责人. '.format(self.post['user_name']))

    def sudo_delete(self):
        sudo_info = Sudo.get_by_id(self.get['id'])
        if not sudo_info:
            raise SupportError(u'删除sudo失败, id不存在: {0}'.format(self.get['id']))
        else:
            return dict(sudo_info=sudo_info)

    def sudo_update(self):
        if not Sudo.query.get(self.get.get('id')):
            raise SupportError(u'更新sudo失败, id不存在: {0}'.format(self.get['id']))

    def sudo_info(self):
        host_info = HostCache.fetch_host(self.get['host_ip'])
        if not host_info:
            raise SupportError('Host not exist in jumper system')
        return dict(host_info=host_info)

    def sudo_cache(self):
        host_info = HostCache.fetch_host(self.get['host_ip'])
        if not host_info:
            raise SupportError('Host not exist in jumper system')
        return dict(host_info=host_info)

    def sudo_config(self):
        host_info = HostCache.fetch_host(self.get['host_ip'])
        if not host_info:
            raise SupportError('Host not exist in jumper system')
        return dict(host_info=host_info)

    def user_add(self):
        if User.get_by(login_name=self.post['user_name']):
            raise SupportError(u'用户已经存在')
        elif User.get_by(uid=self.post.get('uid')):
            raise SupportError(u'用户已经存在')

    def user_delete(self):
        user_info = User.get_by(uid=self.get['id'])
        if not user_info:
            raise SupportError(u'id不存在: {0}'.format(self.get['id']))
        else:
            return dict(user_info=user_info[0])

    def user_update(self):
        user_info = User.get_by(uid=self.get.get('id'))
        if not user_info:
            raise SupportError(u'用户不存在')
        else:
            return dict(user_info=user_info[0])

    def user_reset_password(self):
        user_info = User.get_by(login_name=self.post['user_name'])
        if not user_info:
            raise SupportError(u'用户不存在')
        else:
            return dict(user_info=user_info[0])

    def nss(self):
        if self.get.get('uid'):
            return dict(user_info=get_user(uid=self.get['uid']))
        elif self.get.get('user_name'):
            return dict(user_info=get_user(login_name=self.get['user_name']))
        elif self.get.get('gid'):
            return dict(group_info=Group.get_by_id(self.get['gid']) or get_user(uid=self.get['gid']))
        elif self.get.get('group_name'):
            group_info = Group.get_by(group_name=self.get['group_name'], first=True)
            if not group_info:
                group_info = get_user(login_name=self.get['group_name'])
            return dict(group_info=group_info)

    def command_history_delete(self):
        if len(self.get) < 2:
            raise SupportError(u'参数个数不得少于2')


class ValidationRequestData(object):
    """ 数据结构验证
    """
    def __init__(self, **kw):
        self.required = kw.get('required', [])
        self.length = kw.get('length', {})
        self.optional = kw.get('optional', [])
        self.override = kw.get('override', {})
        self.param_type = kw.get('param_type', {})
        self.one_of = kw.get('one_of', {})
        self.exclude_string = kw.get('exclude_string', {})
        self.repeat = kw.get('repeat', [])
        self.empty = kw.get('empty', [])
        self.chain = [
            self.empty_params,
            self.permit_params,
            self.override_params,
            self.type_params,
            self.one_of_options,
            self.exclude_string_params,
            self.repeat_params,
            self.length_params
        ]

    @staticmethod
    def process(request_data, name=False):
        rule = rules.get(name, dict())
        if not rule:
            return True

        for k in rule:
            if k == 'post':
                [p(data=request_data.get('post', dict())) for p in ValidationRequestData(**rule[k]).chain]
            elif k == 'get':
                [p(data=request_data.get('get', dict())) for p in ValidationRequestData(**rule[k]).chain]
            elif request_data.get('post', dict()).get(k, False):
                data = request_data['post'][k]
                if isinstance(data, list):
                    [p(data=d) for p in ValidationRequestData(**rule[k]).chain for d in data]
                else:
                    [p(data=data) for p in ValidationRequestData(**rule[k]).chain]

    def empty_params(self, **kw):
        for k, v in kw['data'].items():
            if k in self.empty:
                continue
            if isinstance(v, type(None)) or v == '':
                del kw['data'][k]

    def permit_params(self, **kw):
        for i in self.required:
            if i not in kw['data']:
                raise ValidationError(i + ' is required!')

        for k, v in kw['data'].items():
            if k not in self.required + self.optional and k != 'request_json':
                del kw['data'][k]

    def override_params(self, **kw):
        override = {}
        for k, v in self.override.items():
            override[k] = v() if hasattr(v, '__call__') else v
        kw['data'].update(override)

    def type_params(self, **kw):
        for k, v in self.param_type.items():
            if k in kw['data'] and not isinstance(kw['data'][k], v):
                raise ValidationError('%s is not a %s' % (k, v))

    def one_of_options(self, **kw):
        for k, v in self.one_of.items():
            if k in kw['data'] and kw['data'][k] not in v:
                raise ValidationError('the %s is not in %s' % (k, v))

    def exclude_string_params(self, **kw):
        for k, v in self.exclude_string.items():
            if k in kw['data'] and re.search(v, kw['data'][k]):
                raise ValidationError('the %s is Illegal %s' % (k, v))

    def repeat_params(self, **kw):
        for i in self.repeat:
            if i in kw['data'] and len(kw['data'][i]) != len(set(kw['data'][i])):
                raise ValidationError('the "%s" is repeat' % i)

    def length_params(self, **kw):
        for i in self.length:
            if (len(kw['data'][i]) < self.length[i][0]) or (len(kw['data'][i]) > self.length[i][-1]):
                raise ValidationError('the "%s" is length' % i)
