# -*- coding: utf-8 -*-

from datetime import datetime
from flask_script import Command

from app.main import app
from app.models import *
from app.nss.utlis import flush_user
from app.nss.nss_cache import NssCache
from app.sudo.sudo_cache import SudoCache
from app.host.host_cache import HostCache


class FlushNSS(Command):
    @classmethod
    def run(cls):
        with app.app_context():
            st = datetime.now()
            app.logger.info(u'执行nss缓存更新命令')
            user_list = flush_user()
            group_list = Group.get_by(type='sudo')
            NssCache(user_list=user_list, group_list=group_list, smoke=True).update_nss_cache()
            app.logger.info(u'命令执行完成, 共耗时: {0}'.format(datetime.now() - st))


class FlushHost(Command):
    @classmethod
    def run(cls):
        with app.app_context():
            st = datetime.now()
            app.logger.info(u'执行host缓存更新命令')
            HostCache.make_cache()
            app.logger.info(u'命令执行完成, 共耗时: {0}'.format(datetime.now() - st))


class FlushSudo(Command):
    @classmethod
    def run(cls):
        with app.app_context():
            st = datetime.now()
            app.logger.info(u'执行sudo缓存更新命令')
            SudoCache.make_cache()
            app.logger.info(u'命令执行完成, 共耗时: {0}'.format(datetime.now() - st))


class UpgradeCache(Command):
    # nss缓存中移除非sudo组升级使用
    @classmethod
    def run(cls):
        with app.app_context():
            st = datetime.now()
            app.logger.info(u'执行sudo类型group缓存更新命令')
            group = Group.get_by()
            for g in group:
                if g['group_name'].startswith('sudo_sankuai'):
                    Group.update(g, data=dict(type='sudo'))
                    Mapper.update(query=dict(group_name=g['group_name']), data=dict(type='sudo'))
                else:
                    Group.update(g, data=dict(type='auth'))
                    Mapper.update(query=dict(group_name=g['group_name']), data=dict(type='auth'))
            dp_group = Group.query_in("group_name", ["dp_op", "dp_cat"])
            for dp in dp_group:
                Group.update(dp, data=dict(type='sudo'))
                Mapper.update(query=dict(group_name=dp['group_name']), data=dict(type='sudo'))
            app.logger.info(u'命令执行完成, 共耗时: {0}'.format(datetime.now() - st))


class Config(Command):
    @classmethod
    def run(cls):
        with app.app_context():
            print cls.get_colour(u'当前服务配置文件如下：', colour='green')
            for key in sorted(app.config):
                try:
                    print cls.get_colour(u'  {0:30} =>  {1}'.format(key, app.config[key]), colour='green')
                except:
                    print cls.get_colour('  {0:30} =>  {1}'.format(key, app.config[key]), colour='green')

    @staticmethod
    def get_colour(msg, colour='red'):
        try:
            if colour == 'red':
                return u'\033[31m{0}\033[0m'.format(msg)
            elif colour == 'green':
                return u'\033[32m{0}\033[0m'.format(msg)
            elif colour == 'yellow':
                return u'\033[33m{0}\033[0m'.format(msg)
            else:
                return msg
        except UnicodeDecodeError:
            return msg
