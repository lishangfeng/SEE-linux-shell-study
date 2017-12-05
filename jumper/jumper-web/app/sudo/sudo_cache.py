# -*- coding: utf-8 -*-

import copy
import pickle
from jinja2 import Template
from datetime import datetime
from threading import Thread

from app.main import app
from app.models import Sudo
from app.lib.utlis import concat_tag
from app.lib.app_redis import Rds


class SudoCache(Thread):
    def __init__(self, data, corp=None):
        Thread.__init__(self)
        self.data = data
        self.corp = corp
        self.daemon = True

    def run(self):
        with app.app_context():
            _data = self.data
            if self.corp == 'dianping':
                for app_name in _data['data']:
                    result = Sudo.get_by(label_key=app_name)
                    if result:
                        _copy = copy.deepcopy(result)
                        for i in _copy:
                            if i.get('life_cycle') and i['life_cycle'] < datetime.now():
                                result.remove(i)
                                Sudo.delete(**i)
                        if result:
                            app.logger.info(u'更新 sudo 缓存: {0}'.format(app_name))
                            Rds.router().set_sudo(app_name, pickle.dumps(result))
                    else:
                        app.logger.info(u'删除 sudo 缓存: {0}'.format(app_name))
                        Rds.router().del_sudo(app_name)
            else:
                result = Sudo.get_by(label_key=_data['label_key'])
                if result:
                    _copy = copy.deepcopy(result)
                    for i in _copy:
                        if i.get('life_cycle') and i['life_cycle'] < datetime.now():
                            result.remove(i)
                            Sudo.delete(**i)
                    if result:
                        app.logger.info(u'更新 sudo 缓存: {0}'.format(result))
                        Rds.router().set_sudo(_data['label_key'], pickle.dumps(result))
                else:
                    app.logger.info(u'删除 sudo 缓存: {0}'.format(_data))
                    Rds.router().del_sudo(_data['label_key'])

    @staticmethod
    def make_cache():
        """ 
        :return: 刷新所以sudo缓存
        """
        all_data = Sudo.get_by()
        key_list = dict()
        for i in all_data:
            if i.get('life_cycle') and i['life_cycle'] < datetime.now():
                continue
            if not key_list.get(i['label_key']):
                key_list[i['label_key']] = []
            key_list[i['label_key']].append(i)

        new_key_list = dict()
        for key, value in key_list.items():
            new_key_list['sudo_{0}'.format(key)] = value

        # delete useless key
        _all_keys = Rds.router(readonly=True).all_sudo_key()

        for k in _all_keys:
            if k not in new_key_list:
                Rds.router().delete(k)

        # update key value
        for k, v in new_key_list.items():
            Rds.router().set(k, pickle.dumps(v))

    @classmethod
    def fetch_cache(cls, host_info):
        check_order = []

        # store sudo items
        user_sudoer = []
        group_sudoer = []

        sudo_prefix = 'sudo_{0}'
        corp = host_info['corp']
        if corp == 'dianping':
            check_order.insert(0, sudo_prefix.format(host_info['host_ip']))
            check_order.insert(0, sudo_prefix.format(host_info['srv']))

            # fetch all data onetime
            result = Rds.router(readonly=True).mget(*check_order)
            # remove None
            cls.remove_none(result)

            for one in result:
                one = pickle.loads(one)
                for s in one:
                    # s = pickle.loads(o)
                    if s['role'] == 'dp_user':
                        if s['life_cycle'] is None or s['life_cycle'] > datetime.now():
                            user_sudoer.append(s)
                        else:
                            Sudo.delete(**s)
                    if s['role'] == 'dp_group':
                        if s['life_cycle'] is None or s['life_cycle'] > datetime.now():
                            group_sudoer.append(s)
                        else:
                            Sudo.delete(**s)
            else:
                return cls.template(user_sudoer, group_sudoer)

        # generate check order
        for tag in ['owt', 'pdl', 'srv', 'cluster']:
            if host_info.get(tag, None):
                label_key = concat_tag(host_info, tag)
                if not label_key:
                    break
                check_order.insert(0, sudo_prefix.format(label_key))
        else:
            check_order.insert(0, sudo_prefix.format(host_info['host_ip']))
            check_order.insert(0, sudo_prefix.format(host_info['host_fqdn']))

        # exclude conflict
        unique_item = []
        unique_group_name = []

        # fetch all data onetime
        result = Rds.router(readonly=True).mget(*check_order)

        # remove None
        cls.remove_none(result)

        for one in result:
            one = pickle.loads(one)
            for s in one:
                # 内容相同的sudo配置
                _t = '{0}.{1}.{2}.{3}.{4}'
                unique = _t.format(s['role_name'], s['hosts'], s['users'], s['password_option'], s['commands'])
                if unique in unique_item:
                    continue

                # unique_group_name.append(s['role_name'])

                # user items
                if s['role'] == 'user':
                    if s['life_cycle'] is None or s['life_cycle'] > datetime.now():
                        unique_item.append(unique)
                        user_sudoer.append(s)
                    else:
                        Sudo.delete(**s)

                # group items
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
        return cls.template(user_sudoer, group_sudoer, corp)

    @staticmethod
    def template(user_sudoer=list(), group_sudoer=list(), corp='dianping'):

        template = Template("""# Generated {{ time }}
{{ u_str }}{{ g_str }}""")
        g_str = ""
        u_str = ""

        if not len(user_sudoer) and not len(group_sudoer):
            if corp == 'meituan':
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
        if corp == 'dianping':
            _l = "%{0}  {1}=({2}) {3}: {4}\n"
            for i in app.config['SUDO_GROUP']:
                g_str += _l.format(i, 'ALL', 'ALL', 'NOPASSWD', 'ALL')

        timestamp = str(datetime.now()).split('.')[0]
        return template.render(time=timestamp, u_str=u_str, g_str=g_str)

    @staticmethod
    def remove_none(data):
        _none = copy.deepcopy(data)
        for i in _none:
            if i is None:
                data.remove(i)
