# -*- coding: utf-8 -*-

import re
from jinja2 import Template
from datetime import datetime

from app.main import app
from app.models import Sudo
from app.lib.utlis import concat_tag


class SudoConfig:
    def __init__(self, host_info):
        self.result = None
        self.host_info = host_info
        self.corp = host_info['corp']
        self.process()

    def process(self):
        host_info = self.host_info

        check_order = []

        # store sudo items
        user_sudoer = []
        group_sudoer = []
        if self.corp == 'dianping':
            data = Sudo.get_by(label='dp_host', label_key=host_info['host_ip'])
            for i in data:
                if i['role'] == 'dp_user':
                    if i['life_cycle'] is None or i['life_cycle'] > datetime.now():
                        user_sudoer.append(i)
                    else:
                        Sudo.delete(**i)
                if i['role'] == 'dp_group':
                    if i['life_cycle'] is None or i['life_cycle'] > datetime.now():
                        group_sudoer.append(i)
                    else:
                        Sudo.delete(**i)
            data = Sudo.get_by(label='dp_project', label_key=host_info['srv'])
            for i in data:
                if i['role'] == 'dp_user':
                    if i['life_cycle'] is None or i['life_cycle'] > datetime.now():
                        user_sudoer.append(i)
                    else:
                        Sudo.delete(**i)
                if i['role'] == 'dp_group':
                    if i['life_cycle'] is None or i['life_cycle'] > datetime.now():
                        group_sudoer.append(i)
                    else:
                        Sudo.delete(**i)
            self.template(user_sudoer, group_sudoer)
            return

        check_order.append(dict(label='host_ip', label_key=host_info['host_ip']))
        check_order.append(dict(label='host_fqdn', label_key=host_info['host_fqdn']))
        for tag in ['cluster', 'srv', 'pdl', 'owt', 'corp']:
            if host_info.get(tag, None):
                label_key = concat_tag(host_info, tag)
                if not label_key:
                    break
                check_order.append(dict(label=tag, label_key=label_key))

        # exclude conflict
        unique_item = []
        unique_group_name = []

        for i in check_order:
            sudo_rules = Sudo.get_by(label=i['label'], label_key=i['label_key'])
            for s in sudo_rules:
                # 内容相同的sudo配置
                _t = '{0}.{1}.{2}.{3}.{4}'
                unique = _t.format(s['role_name'], s['hosts'], s['users'], s['password_option'], s['commands'])
                if unique in unique_item:
                    continue
                if s['role'] == 'user':
                    if s['life_cycle'] is None or s['life_cycle'] > datetime.now():
                        unique_item.append(unique)
                        user_sudoer.append(s)
                    else:
                        Sudo.delete(**s)
                if s['role'] == 'group':
                    if unique_group_name and s['role_name'] not in unique_group_name:
                        for x in unique_group_name:
                            if not x.startswith(s['role_name']):  # meituan.sre.inf存在，则丢弃meituan.sre的记录
                                if s['life_cycle'] is None or s['life_cycle'] > datetime.now():
                                    group_sudoer.append(s)
                                    unique_item.append(unique)
                                    unique_group_name.append(s['role_name'])
                                else:
                                    Sudo.delete(**s)
                    else:  # 组同名但授权内容不同
                        if s['life_cycle'] is None or s['life_cycle'] > datetime.now():
                            group_sudoer.append(s)
                            unique_item.append(unique)
                            unique_group_name.append(s['role_name'])
                        else:
                            Sudo.delete(**s)

        self.template(user_sudoer, group_sudoer)

    def template(self, user_sudoer=list(), group_sudoer=list()):

        template = Template("""# Generated {{ time }}
{{ u_str }}{{ g_str }}""")
        g_str = ""
        u_str = ""

        if not len(user_sudoer) and not len(group_sudoer):
            if self.corp == 'meituan':
                return None

        # pack user part
        for i in user_sudoer:
            _l = "{0}  {1}=({2}) {3}: {4}\n"
            u_str += _l.format(i['role_name'], i['hosts'], i['users'], i['password_option'], i['commands'])

        # pack group part
        for j in group_sudoer:
            _l = "%{0}  {1}=({2}) {3}: {4}\n"
            g_str += _l.format(j['role_name'], j['hosts'], j['users'], j['password_option'], j['commands'])

        # dp_op default privileges
        if self.corp == 'dianping':
            _l = "%{0}  {1}=({2}) {3}: {4}\n"
            for i in app.config['SUDO_GROUP']:
                g_str += _l.format(i, 'ALL', 'ALL', 'NOPASSWD', 'ALL')

        timestamp = str(datetime.now()).split('.')[0]
        self.result = template.render(time=timestamp, u_str=u_str, g_str=g_str)
