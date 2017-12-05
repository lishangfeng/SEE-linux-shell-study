# -*- coding: utf-8 -*-

import copy
from jinja2 import Template
from datetime import datetime
from datetime import timedelta

from app.main import app
from app.models import Sudo
from app.lib.utlis import concat_tag
from app.lib.database import db
from app.lib.error_define import SupportError


class SudoInfo:
    """pack sudo info"""
    def __init__(self, data):
        self.data = data
        self.project_name = None
        self.user_id = data['get']['user_id']
        self.host_ip = data['get']['host_ip']
        self.host_name = data['get']['host_name']
        self.host_info = data['host_info']

        self.user_set = list()
        self.group_set = list()

        self.temp_list = list()
        self.order_list = list()

    def process(self):
        # user login with root privilege
        if int(self.user_id) != 0:
            return False

        if self.host_info['corp'] == 'dianping':
            self.project_name = self.host_info['srv']
            return self.dp()
        else:
            return self.mt()

    def mt(self):
        self.order_list.append(dict(label='host_ip', label_key=self.host_info['host_ip']))
        self.order_list.append(dict(label='host_fqdn', label_key=self.host_info['host_fqdn']))

        for tag in ['corp', 'owt', 'pdl', 'srv', 'cluster']:
            if self.host_info.get(tag, None):
                label_key = concat_tag(self.host_info, tag)
                if not label_key:
                    break
                self.temp_list.append(dict(label=tag, label_key=label_key))
        self.order_list = self.order_list + self.temp_list[::-1]

        # 记录同一层级下相同授权记录
        sudo_user = []
        sudo_group = []
        group_name = []
        # 根据树结构, 从底层往上递归, 底层存在的相同授权优先级高于最上层
        for item in self.order_list:
            data = Sudo.query.filter_by(role='user', label=item['label'], label_key=item['label_key']).all()
            if not data:
                continue
            for user in data:
                # 用户sudo授权无继承关系,可以整条命令记录才作为判断依据
                sudo_item = '{0}.{1}.{2}.{3}.{4}'.format(user.role_name, user.hosts, user.users, user.password_option, user.commands)
                if sudo_item not in sudo_user:
                    if user.life_cycle is None or user.life_cycle > datetime.now():
                        self.user_set.append(user.to_dict())
                        sudo_user.append(sudo_item)

        for item in self.order_list:
            data = Sudo.query.filter_by(role='group', label=item['label'], label_key=item['label_key']).all()
            if not data:
                continue
            for group in data:
                # 即使
                sudo_item = '{0}.{1}.{2}.{3}.{4}'.format(group.role_name, group.hosts, group.users, group.password_option, group.commands)
                if sudo_item not in sudo_group: # 过滤相同的sudo授权
                    if group.role_name not in group_name: # 过滤组同名的sudo授权
                        if not len(group_name):  # 组为空直接存入数据
                            if group.life_cycle is None or group.life_cycle > datetime.now():
                                sudo_group.append(sudo_item)
                                group_name.append(group.role_name)
                                self.group_set.append(group.to_dict())
                                continue
    
                        for x in group_name:   # 组不为空,  以startswith校验是否同一层级
                            if not x.startswith(group.role_name):
                                if group.life_cycle is None or group.life_cycle > datetime.now():
                                    sudo_group.append(sudo_group)
                                    group_name.append(group.role_name)
                                    self.group_set.append(group.to_dict())
                    else:  # 组同名但授权内容不同
                        if group.life_cycle is None or group.life_cycle > datetime.now():
                            self.group_set.append(group.to_dict())
                            sudo_group.append(sudo_item)

        return self.mt_template()

    def dp(self):
        # 点评扁平化sudo授权, 只对host_ip或者project进行授权
        for label in ['dp_host', 'dp_project']:
            for label_key in [self.host_ip, self.project_name]:
                data = Sudo.query.filter_by(role='dp_user', label=label, label_key=label_key).all()
                if not data:
                    continue
                for user in data:
                    if user.life_cycle is None or user.life_cycle > datetime.now():
                        self.user_set.append(user.to_dict())

        for label in ['dp_host', 'dp_project']:
            for label_key in [self.host_ip, self.project_name]:
                data = Sudo.query.filter_by(role='dp_group', label=label, label_key=label_key).all()
                if not data:
                    continue
                for group in data:
                    if group.life_cycle is None or group.life_cycle > datetime.now():
                        self.group_set.append(group.to_dict())

        return self.dp_template()

    def mt_template(self):
        template = Template("""# Generated {{ time }}
{{ cmd_alias_string }}
{{ user_string }}{{ group_string }}""")
        cmd_alias_string = ""
        group_string = ""
        user_string = "# Users and Groups privileges\n"

        # 排除相同Cmnd_Alias
        cmd_alias = []

        if len(self.user_set):
            for v in self.user_set:
                command_alias = "Cmnd_Alias  {0}_{1}_{2}={3}\n".format(
                                v['role'].upper(),
                                v['role_name'].upper().replace(".", "_").replace("-", "_"),
                                v['label'].upper(),
                                v['commands'])

                user_line = "{0}  {1}=({2}) {3}: {4}_{5}_{6}\n".format(
                                v['role_name'],
                                v['hosts'],
                                v['users'],
                                v['password_option'],
                                v['role'].upper(),
                                v['role_name'].upper().replace(".", "_").replace("-", "_"),
                                v['label'].upper())
                if command_alias not in cmd_alias:
                    cmd_alias_string += command_alias
                    cmd_alias.append(command_alias)
                user_string += user_line

        if len(self.group_set):
            for v in self.group_set:
                command_alias = "Cmnd_Alias  {0}_{1}_{2}={3}\n".format(
                                v['role'].upper(),
                                v['role_name'].upper().replace(".", "_").replace("-", "_"),
                                v['label'].upper(),
                                v['commands'])

                group_line = "%{0}  {1}=({2}) {3}: {4}_{5}_{6}\n".format(
                            v['role_name'],
                            v['hosts'],
                            v['users'],
                            v['password_option'],
                            v['role'].upper(),
                            v['role_name'].upper().replace(".", "_").replace("-", "_"),
                            v['label'].upper())
                if command_alias not in cmd_alias:
                    cmd_alias_string += command_alias
                    cmd_alias.append(command_alias)
                group_string += group_line
        # 无数据即返回空字符串, 便于客户端识别
        if not len(cmd_alias_string):
            return ' '

        timestamp = str(datetime.now()).split('.')[0]
        return template.render(time=timestamp,
                               cmd_alias_string=cmd_alias_string,
                               user_string=user_string,
                               group_string=group_string)

    def dp_template(self):
        template = Template("""# Generated {{ time }}
{{ cmd_alias_string }}
{{ user_string }}{{ group_string }}""")
        cmd_alias_string = ""
        group_string = ""
        user_string = "# Users and Groups privileges\n"

        # 排除相同Cmnd_Alias
        cmd_alias = []

        if len(self.user_set):
            for v in self.user_set:
                command_alias = "Cmnd_Alias  {0}_{1}_{2}={3}\n".format(
                                v['role'].upper(),
                                v['role_name'].upper().replace(".", "_").replace("-", "_"),
                                v['label'].upper(),
                                v['commands'])

                user_line = "{0}  {1}=({2}) {3}: {4}_{5}_{6}\n".format(
                                v['role_name'],
                                v['hosts'],
                                v['users'],
                                v['password_option'],
                                v['role'].upper(),
                                v['role_name'].upper().replace(".", "_").replace("-", "_"),
                                v['label'].upper())
                if command_alias not in cmd_alias:
                    cmd_alias_string += command_alias
                    cmd_alias.append(command_alias)
                user_string += user_line

        if len(self.group_set):
            for v in self.group_set:
                command_alias = "Cmnd_Alias  {0}_{1}_{2}={3}\n".format(
                                v['role'].upper(),
                                v['role_name'].upper().replace(".", "_").replace("-", "_"),
                                v['label'].upper(),
                                v['commands'])

                group_line = "%{0}  {1}=({2}) {3}: {4}_{5}_{6}\n".format(
                            v['role_name'],
                            v['hosts'],
                            v['users'],
                            v['password_option'],
                            v['role'].upper(),
                            v['role_name'].upper().replace(".", "_").replace("-", "_"),
                            v['label'].upper())
                if command_alias not in cmd_alias:
                    cmd_alias_string += command_alias
                    cmd_alias.append(command_alias)
                group_string += group_line

        # 角色, sa, op, sre授权
        group_string += "\n# Default Groups privileges\n"
        for super_group in app.config.get('SUDO_GROUP', []):
            group_line = "%{0}  {1}=({2}) {3}: {4}\n".format(
                        super_group,
                        'ALL',
                        'ALL',
                        'NOPASSWD',
                        'ALL')
            group_string += group_line

        # 次级用户, 部分sudo权限
        group_string += "\n# Minor Groups privileges\n"
        if app.config.get('MINOR_PRIVILEGE'):
            group_line = "%{0}  {1}=({2}) {3}: {4}\n".format(
                            'dp_minor',
                            'ALL',
                            'root,nobody',
                            'NOPASSWD',
                            str(app.config.get('MINOR_PRIVILEGE')))
            group_string += group_line

        timestamp = str(datetime.now()).split('.')[0]
        return template.render(time=timestamp,
                               cmd_alias_string=cmd_alias_string,
                               user_string=user_string,
                               group_string=group_string)


class AddSudo:
    """ add sudo for shanghai """
    def __init__(self, data):
        self.request = data['post']
        self.life_cycle = datetime.now() + timedelta(days=1)
        self.result = dict(success_hosts=[], failed_hosts=[])

    def process(self, sankuai=None):
        for x in self.request['data']:
            if sankuai:
                try:
                    sudo = Sudo.query.filter(Sudo.role.startswith('dp_')). \
                        filter(Sudo.role_name == self.request['user_name']). \
                        filter(Sudo.label_key == x). \
                        filter(Sudo.users.startswith('sankuai')).first()
                    if sudo:
                        self.result['success_hosts'].append(x)
                        continue
                except Exception as e:
                    app.logger.error(u'更新DB失败: {0}'.format(str(e)))
                    raise SupportError(u'更新DB失败: {0}'.format(str(e)))
                sudo_item = dict(
                    role='dp_user',
                    role_name=self.request['user_name'],
                    users='sankuai',
                    label='',
                    label_key='')
            else:
                try:
                    sudo = Sudo.query.filter(Sudo.role.startswith('dp_')). \
                        filter(Sudo.role_name == self.request['user_name']). \
                        filter(Sudo.label_key == x). \
                        filter(Sudo.users.startswith('root')).first()
                    if sudo and sudo.life_cycle:
                        sudo.life_cycle = self.life_cycle
                        db.session.commit()
                        self.result['success_hosts'].append(x)
                        continue
                except Exception as e:
                    app.logger.error(u'更新DB失败: {0}'.format(str(e)))
                    raise SupportError(u'更新DB失败: {0}'.format(str(e)))
                sudo_item = dict(
                        role='dp_user',
                        role_name=self.request['user_name'],
                        users='root,nobody',
                        label='',
                        label_key='',
                        life_cycle=self.life_cycle)

            sudo_item.update(dict(label='dp_{0}'.format(self.request['sudo_type']), label_key=x))
            if Sudo.insert(**sudo_item):
                self.result['success_hosts'].append(x)
            else:
                self.result['failed_hosts'].append(x)
        user_name = self.request['user_name']
        target_host = self.result['success_hosts']
        app.logger.info(u'新增sudo权限, 用户名:{0}, 作用目标:{1}'.format(user_name, target_host))
        return self.result
