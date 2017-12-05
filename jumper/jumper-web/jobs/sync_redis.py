# -*- coding: utf-8 -*-

import time
import pickle
import socket
from datetime import datetime
from flask_script import Command
from app.lib.notice import Notice
from app.main import app
from app.models import *
from app.nss.nss import Nss
from app.lib.app_redis import Rds
from app.nss.nss_cache import NssCache
from app.sudo.sudo_cache import SudoCache
from app.host.host_cache import HostCache

"""
巡检key:
        host_list，
        user_list,
        heartbeat,
        nss_cache,
        nss_cache_user,
        nss_cache_group,
        commands_history,
        sudo_xxxxx,
"""


def host_list():
    total = 0
    delete_count = 0
    add_count = 1
    hosts_keys = Rds.readonly().hkeys('host_list')
    db_keys = Host.get_by(show='host_ip')
    db_keys = [i['host_ip'] for i in db_keys]
    if hosts_keys and db_keys:
        redis_trash = set(hosts_keys) - set(db_keys)
        for ip in redis_trash:
            Rds.router().del_host(ip)
            delete_count += 1
            app.logger.info(u'清理过期 host_list 数据, IP:{0}'.format(ip))

        incremental = set(db_keys) - set(hosts_keys)
        for ip in incremental:
            host_info = Host.get_by(first=True, host_ip=ip)
            if host_info:
                Rds.router().set_host(host_info)
                add_count += 1
            app.logger.info(u'新增 host_list 数据, IP:{0}'.format(ip))
    elif not hosts_keys and db_keys:
        app.logger.info(u'redis中无 host_list 数据, 开启全量刷缓存')
        total = 1
        HostCache.make_cache()

    host = Host.get_by(show='host_ip')
    uniq = dict()
    repeat_ip = ''
    incremental = 0
    for i in host:
        if not uniq.get(i['host_ip']):
            uniq[i['host_ip']] = 0
        uniq[i['host_ip']] += 1

    for j in uniq:
        if uniq[j] > 1:
            incremental += 1
            repeat_ip += 'count:{0}, IP:{1}\n'.format(uniq[j], j)
    if incremental > 0:
        app.logger.info(u'mysql中 host 表数据存在重复ip, 数量:{0}, 重复数据:{1}'.format(incremental, repeat_ip))

    if total == 1:
        return u'redis中无 host_list 数据, 开启全量刷缓存'
    else:
        return u'新增主机数: {0}, 删除主机数: {1}, 重复IP数: {2}, 重复数据:{3}'.format(add_count, delete_count, incremental, repeat_ip)


def user_list():
    add_user = 0
    delete_user = 0
    user_keys = Rds.readonly().hkeys('user_list')
    db_keys = User.get_by(show='login_name', enable=1)
    db_keys = [i['login_name'] for i in db_keys]
    if user_keys and db_keys:
        redis_trash = set(user_keys) - set(db_keys)
        for user in redis_trash:
            Rds.router().del_user(user)
            delete_user += 1
            app.logger.info(u'清理过期 user_list 数据, user_name:{0}'.format(user))

        incremental = set(db_keys) - set(user_keys)
        for user in incremental:
            user_info = User.get_by(first=True, login_name=user)
            if user_info:
                Rds.router().set_user(user_info)
                add_user += 1
            app.logger.info(u'新增 user_list 数据, user_name:{0}'.format(user_info['login_name']))
    elif not user_keys and db_keys:
        app.logger.info(u'redis中无 user_list 数据, 开启全量刷缓存')
        users = User.get_by(enable=1)
        for user in users:
            Rds.router().set_user(user)

    return u'新增用户数: {0}, 删除用户数: {1}'.format(add_user, delete_user)


def heartbeat():
    """
        1，对比session数据和heartbeat数据

        login_uuid_cb1e6df0-e383-40a2-9ad7-649fe2f4c64c
        alex.wan:3fbe0ad5-65b3-41a0-ae1a-8ec595e66e5e
    """
    count = 0
    keys = [k for k in Rds.router().scan_iter(match='login_uuid_{0}'.format('*'), count=500)]
    login_uuid = set([i[11:] for i in keys])
    user_map = {}
    for i in Rds.router().hkeys('heartbeat'):
        user, uuid = i.split(':')
        user_map[uuid] = user
    heartbeat_keys = set(user_map.keys())
    incremental = heartbeat_keys - login_uuid
    for x in incremental:
        count += 1
        app.logger.info(u'清理 heartbeat 中无用key uuid:{0}'.format(x))
        Rds.router().hdel('heartbeat', '{0}:{1}'.format(user_map[x], x))
    return u'清理heartbeat中无用数: {0}'.format(count)


def nss_cache():
    """
        1，获取version版本
        2，获取存放增量缓存的所有key
        3，不在version版本中的key视为过期key
    """
    count = 0
    data = Rds.readonly().get('nss_cache_version')
    if not data:
        app.logger.warning(u'获取缓存 nss_cache_version 失败, 不进行操作')
        return
    data = pickle.loads(data)
    uuid = [i['version'] for i in data]
    cache_keys = Rds.readonly().hkeys('nss_cache')
    expired_keys = set(cache_keys) - set(uuid)
    for x in expired_keys:
        count += 1
        app.logger.info(u'清理 nss_cache 中过期版本 uuid:{0}'.format(x))
        time.sleep(0.1)  # 避免大量删除导致redis写压力
        Rds.router().hdel('nss_cache', x)
    return u'清理nss_cache中无用key数: {0}'.format(count)


def nss_cache_user():
    """
        1，获取mysql所有账号
        2，获取redis所有缓存账号
        3，对比user所属的group
    """
    leak_users = {}
    user_list = User.get_by()
    user_dict = Rds.readonly().hgetall('nss_cache_user')
    for user_info in user_list:
        try:
            if user_dict.get(user_info['login_name']):
                user = Nss.user(user_info)
                user_cache = pickle.loads(user_dict[user_info['login_name']])
                if set(user['group'].keys()) == set(user_cache['group'].keys()):
                    continue
            leak_users[user_info['login_name']] = user_info
        except Exception as e:
            app.logger.error(u'对比nss_user异常->{0}'.format(str(e)))

    if len(leak_users) <= 30:
        if len(leak_users) == 0:
            app.logger.info(u'没有遗漏用户, 不操作')
        else:
            app.logger.info(u'开始将用户刷新到缓存:{0}'.format(leak_users.keys()))
            NssCache(user_list=leak_users.values()).update_nss_cache()
            app.logger.info(u'刷新完成')
    else:
        app.logger.info(u'用户数量超过限制（30））, 放弃脚本刷新')
    return u'修复nss_cache_user中遗漏账号数: {0}'.format(len(leak_users))


def nss_cache_group():
    """
        1，取mysql中所有sudo组
        2，取redis中所有组
        3，对比group中member

    """
    leak_groups = {}
    group_list = Group.get_by(type='sudo')
    group_dict = Rds.readonly().hgetall('nss_cache_group')

    for group_info in group_list:
        try:
            group = Nss.group(group_info)
            if group_dict.get(group_info['group_name']):
                group_cache = pickle.loads(group_dict[group_info['group_name']])
                if set(group['gr_mem']) == set(group_cache['gr_mem']):
                    continue
            if len(group['gr_mem']) != 0:
                leak_groups[group_info['group_name']] = group_info
        except Exception as e:
            app.logger.error(u'对比nss_group异常->{0}'.format(str(e)))

    if len(leak_groups) <= 30:
        if len(leak_groups) == 0:
            app.logger.info(u'没有遗漏组, 不操作')
        else:
            app.logger.info(u'开始将组刷新到缓存:{0}'.format(leak_groups.keys()))
            NssCache(group_list=leak_groups.values()).update_nss_cache()
            app.logger.info(u'刷新完成')
    else:
        app.logger.info(u'组数量超过限制（30））, 放弃脚本刷新')

    count = 0
    for x in group_dict.values():
        unhash = pickle.loads(x)
        if len(unhash['gr_mem']) == 0:
            count += 1
            Rds.router().hdel('nss_cache_group', unhash['gr_name'])
            app.logger.info(u'删除 nss_cache_group 无member的组, {0}'.format(unhash['gr_name']))
    return u'修复nss_cache_user中遗漏账号数: {0}, 删除无member组:{1}'.format(len(leak_groups), count)


def commands_history():
    """
        1，取redis中所有账号
        2，判断账号是否离职，离职即删除历史命令
    """
    count = 0
    user_keys = Rds.readonly().hkeys('commands_history')
    for user_name in user_keys:
        user_info = User.get_by(show='login_name', enable=1, login_name=user_name)
        if not user_info:
            Rds.router().hdel('commands_history', user_name)
            count += 1
            app.logger.info(u'清除离职账号历史命令 账号:{0}'.format(user_name))
    return u'删除离职人员历史命令数:{0}'.format(count)


def sudo_xxxxx():
    SudoCache.make_cache()


class SyncCache(Command):
    @classmethod
    def run(cls):
        with app.app_context():
            try:
                # host_list
                begin = datetime.now()
                st = datetime.now()
                app.logger.info(u'开始执行 host_list 检查')
                _host_list = host_list()
                app.logger.info(u'完成执行 host_list 检查，耗时：{0}'.format(datetime.now() - st))

                # user_list
                st = datetime.now()
                app.logger.info(u'开始执行 user_list 检查')
                _user_list = user_list()
                app.logger.info(u'完成执行 user_list 检查，耗时：{0}'.format(datetime.now() - st))

                # heartbeat
                st = datetime.now()
                app.logger.info(u'开始执行 heartbeat 检查')
                _heartbeat = heartbeat()
                app.logger.info(u'完成执行 heartbeat 检查，耗时：{0}'.format(datetime.now() - st))

                # nss_cache
                st = datetime.now()
                app.logger.info(u'开始执行 nss_cache 检查')
                _nss_cache = nss_cache()
                app.logger.info(u'完成执行 nss_cache 检查，耗时：{0}'.format(datetime.now() - st))

                # nss_cache_user
                st = datetime.now()
                app.logger.info(u'开始执行 nss_cache_user 检查')
                _nss_cache_user = nss_cache_user()
                app.logger.info(u'完成执行 nss_cache_user 检查，耗时：{0}'.format(datetime.now() - st))

                # nss_cache_group
                st = datetime.now()
                app.logger.info(u'开始执行 nss_cache_group 检查')
                _nss_cache_group = nss_cache_group()
                app.logger.info(u'完成执行 nss_cache_group 检查，耗时：{0}'.format(datetime.now() - st))

                # commands_history
                st = datetime.now()
                app.logger.info(u'开始执行 commands_history 检查')
                _commands_history = commands_history()
                app.logger.info(u'完成执行 commands_history 检查，耗时：{0}'.format(datetime.now() - st))

                # sudo_xxxxx
                st = datetime.now()
                app.logger.info(u'开始执行 sudo_xxxxx 检查')
                sudo_xxxxx()
                app.logger.info(u'完成执行 sudo_xxxxx 检查，耗时：{0}'.format(datetime.now() - st))

                app.logger.info(u'此次job执行总耗时:{0}'.format(datetime.now() - begin))
                app.logger.info('*' * 40)
                message = u""" Jumper Job 执行成功
        执行机器: {0}
        Job名称：SyncCache(Redis缓存数据清理和同步)
        本次同步列表:
            host_list:{1}
            user_list:{2}
            heartbeat:{3}
            nss_cache:{4}
            nss_cache_user:{5}
            nss_cache_group:{6}
            commands_history:{7}
        日志目录: /data/applogs/jumper-web/logs/app.log""".format(socket.gethostname(),
                                                              _host_list,
                                                              _user_list,
                                                              _heartbeat,
                                                              _nss_cache,
                                                              _nss_cache_user,
                                                              _nss_cache_group,
                                                              _commands_history
                                                              )
                Notice(message, app.config['JOB_ADMIN'])
            except Exception as e:
                message = u""" Jumper Job 任务失败
        执行机器: {0}
        Job名称：SyncCache(Redis缓存数据清理和同步)
        日志目录: /data/applogs/jumper-web/logs/app.log
        失败原因: {1}""".format(socket.gethostname(), str(e))
                Notice(message, app.config['JOB_ADMIN'])
