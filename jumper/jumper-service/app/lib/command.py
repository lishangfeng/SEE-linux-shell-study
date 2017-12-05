# -*- coding:utf-8 -*-

import copy
import logging
import os
import re
import subprocess
import sys
import time
from threading import Thread

import paramiko
from app.lib.async import Async
from app.lib.getapp import get_app, get_host
from app.lib.password import Password
from app.lib.sre_config import dir_config
from app.lib.ssh_option import PsshOptions
from app.lib.ssh_option import SshOptions
from app.lib.thread_pool import AsyncThread
from app.lib.thread_pool import ThreadPool
from app.lib.utils import alive_port
from app.lib.utils import get_colour

from app.ssh_server.get_backend import GetBackend
from app.ssh_server.init import command_pids
from app.ssh_server.init import commands_list
from app.ssh_server.init import config
from app.ssh_server.init import ssh_history

reload(sys)
sys.setdefaultencoding("utf-8")


class ShellCommand:
    def __init__(self):
        pass

    @staticmethod
    def user_info(channel, user_info):
        order = ['role', 'name', 'uid', 'gid', 'shell', 'mobile', 'login_name',
                 'home_dir', 'email', 'login_time', 'register_time', 'password_mtime']
        data = [u'{0}: {1}'.format(k, user_info[k]) for k in order]
        channel.sendall(get_colour('\r\n'.join(data), colour='green') + '\r\n')

    @staticmethod
    def user_id(command, channel, user_info):
        command = [i for i in command.split(' ') if i]
        if len(command) == 2:
            user_info = Async.get_user(dict(login_name=command[-1]))
        if not user_info:
            channel.sendall(get_colour(u'该用户不存在\r\n'))
        else:
            order = ['role', 'name', 'uid', 'gid', 'shell', 'mobile', 'login_name',
                     'home_dir', 'email', 'login_time', 'register_time', 'password_mtime']
            data = [u'{0}: {1}'.format(k, user_info[k]) for k in order]
            channel.sendall(get_colour('\r\n'.join(data), colour='green') + '\r\n')

    @staticmethod
    def r(channel, user_uid):
        login_history = Async.get_login(user_uid)
        if login_history is None:
            channel.sendall(get_colour(u'哎哟, 接口出现异常未能获得数据\r\n', colour='green'))
        elif not len(login_history):
            channel.sendall(get_colour(u'您最近没有登录历史哦\r\n', colour='green'))
        else:
            del ssh_history[:]
            channel.sendall(get_colour(u'登录名\t\t登录时间\t\t快捷键\t主机名\r\n', colour='green'))
            for index, i in enumerate(login_history):
                ssh_history.append(i)
                short_cut = ' r{0}'.format(index+1)
                login_name = i.get('login_name') or i['user_name']
                if len(login_name) < 5:
                    login_name = login_name + '\t'
                strings = '{0}\t{1}\t{2}\t{3}\r\n'.format(login_name, i['login_time'], short_cut, i['host_name'])
                channel.sendall(get_colour(strings, colour='green'))

    @staticmethod
    def check_user_info(channel, connection_info):
        order = ['pid', 'name', 'user_id', 'login_name', 'client_port', 'client_ip', 'server_name', 'uuid']
        data = [u'{0}: {1}'.format(k, connection_info[k]) for k in order]
        channel.sendall(get_colour('\r\n'.join(data), colour='green') + '\r\n')

    @staticmethod
    def password(status, terminal, channel, user_info, jumper):
        password_expired = jumper.proxy_server.password_expired
        password_reset = jumper.proxy_server.password_reset
        password_retry = jumper.proxy_server.password_retry
        channel.sendall(u'更新用户{0} 的密码\r\n'.format(user_info['login_name']))
        new_password = terminal.get_password(status, channel, u'新密码: ')
        if not new_password:
            channel.sendall(get_colour(u'密码不允许为空\r\n'))
        elif new_password == '^C':
            if password_expired or password_reset:
                jumper.close()
                os.kill(os.getpid(), 15)
                return True
            channel.sendall('^C\r\n')
        elif len(new_password) < 8 or len(new_password) > 35:
            channel.sendall(get_colour(u'密码长度限制: < 8 password > 35\r\n'))
        elif not Password.password_complex(new_password):
            channel.sendall(
                get_colour(u'密码必须至少包括其中三种: 数字, 大写字母, 小写字母, 特殊字符(^ $ . ? ! @ = + - % * &)\r\n'))
        elif Password.check_password(user_info, new_password):
            channel.sendall(get_colour(u'不能重复,请使用新密码\r\n'))
        elif Password.check_history(user_info['old_password_dict'], new_password):
            channel.sendall(get_colour(u'密码在过去三次修改中使用,请使用别的密码\r\n'))
        elif new_password == terminal.get_password(status, channel, u'确认新密码: '):
            _data = dict(password=new_password)
            Async.update_password(dict(uid=user_info['uid']), data=_data)
            new_user_info = Async.get_user(dict(uid=user_info['uid']))
            jumper.user_info.update(new_user_info)
            password_expired = jumper.proxy_server.password_expired = False
            password_reset = jumper.proxy_server.password_reset = False
            password_retry = jumper.proxy_server.password_retry = 0
            channel.sendall(get_colour(u'身份验证令牌已经成功更新\r\n', colour='green'))
            if not password_expired and not password_reset:
                channel.sendall(jumper.user_navigation)
            logging.info(u'{0} 更新密码成功'.format(user_info['login_name']))
        else:
            channel.sendall(get_colour(u'两次输入密码不一致\r\n'))
        if password_expired or password_reset:
            if password_retry == 1:
                channel.sendall(u'Ctrl+C退出, 继续请回车...')
            # 密码重试超过2次退出
            elif password_retry == 2:
                channel.sendall(get_colour(u'\r\n2次修改密码失败, 系统退出.\r\n\n', colour='yellow'))
                jumper.close()
                os.kill(os.getpid(), 15)
                return True
        else:
            channel.sendall(terminal.user_ps1)

    @staticmethod
    def ssh(jumper, channel, command, sync_lock):
        ssh_option = SshOptions(command)
        if ssh_option.status:
            session_expired = None
            if not ssh_option.info.get('user_name') or ssh_option.info.get('user_name') == jumper.user_name:
                if not Async.get_uuid(config['uuid'], jumper.user_info['source']):
                    channel.sendall(get_colour('当前终端会话已失效,输入kinit命令恢复会话或输入密码登录(ctrl+c取消密码输入)\r\n'))
                    session_expired = True
            jumper.status[channel] = 1
            ThreadPool(worker=GetBackend, ssh_option=ssh_option.info, jumper=jumper, proxy_channel=channel, session_expired=session_expired, sync_lock=sync_lock)
            return True
        else:
            channel.sendall(get_colour(ssh_option.help, colour='green'))
            channel.sendall(jumper.user_ps1)

    @staticmethod
    def info(channel, connection_info):
        info = copy.deepcopy(connection_info)
        info['channel_id'] = channel.get_id()
        order = ['pid', 'name', 'channel_id', 'session_type', 'user_id',
                 'login_name', 'client_port', 'client_ip', 'server_name', 'uuid']
        data = [u'{0}: {1}'.format(k, info[k][9:] if k == 'uuid' else info[k]) for k in order]
        channel.sendall(get_colour('\r\n'.join(data), colour='green') + '\r\n')

    @staticmethod
    def config(channel):
        channel.sendall(get_colour(dir_config(), colour='green'))

    @staticmethod
    def getapp(channel, command):
        help = """
    机器在哪里申请用哪里的查询方式!!!\r\n
    上海研发以cmdb应用名为查询维度\r
    用法: getapp app_name\r
    例子: getapp shop-web\r

    北京研发以ops服务树label为查询维度\r
    用法: getapp owt.pdl.srv 或者 getapp owt.pdl.srv.cluster(指定环境查看)\r
    例子: getapp sre.jumper.service\r
    例子: getapp sre.jumper.service.staging\r\n\n"""
        command_split = [i for i in command.split(' ') if i]
        if len(command_split) != 2:
            if len(command_split[0]) == len('getapp'):
                channel.sendall(get_colour(help, colour='green'))
            else:
                channel.sendall(get_colour(u'命令{0}不存在, 键入 H 查看帮助信息').format(command) + '\r\n')
            return True
        try:
            result, t = get_app(command_split[1])
        except Exception as e:
            channel.sendall(get_colour(u'未知错误: {0}'.format(str(e))) + '\r\n')
            return True

        if isinstance(result, list):
            if t == 'shanghai':
                s = u''
                for i in result:
                    # s += u'{name:25} {ip:15}{cpu:5}    {memory:5}{env:8}{idc}\n\r'.format(**i)
                    s += u'{idc:8} {cpu:2}核 {memory:5}{env:10} {ip:15} {name:25}\n\r'.format(**i)
                channel.sendall(get_colour(s, colour='green') + '\r')
            elif t == 'beijing':
                s = u''
                for i in result:
                    s += u'{idc} {cpu:2}核 {memory:5} {cluster:16} {ip:15} {name:25}  \n\r'.format(**i)
                channel.sendall(get_colour(s, colour='green') + '\r')
        else:
            channel.sendall(get_colour(result + '\r\n'))

    @staticmethod
    def gethost(channel, command):
        help = """
    请注意使用gethost的正确姿势！！！\r\n
    用法: gethost ip 或 hostname\r\n
    例子: gethost 10.3.16.5\r
    例子: gethost shop-web01.nh\r
    例子: gethost dx-sys-ops01\r
    例子: gethost dx-sys-ops01.dx.sankuai.com\r\n\n"""

        command_split = [i for i in command.split(' ') if i]
        if len(command_split) != 2:
            if len(command_split[0]) == len('gethost'):
                channel.sendall(get_colour(help, colour='green'))
            else:
                channel.sendall(get_colour(u'命令{0}不存在, 键入 H 查看帮助信息').format(command) + '\r\n')
            return True
        try:
            result = get_host(command_split[1])
        except Exception as e:
            channel.sendall(get_colour(u'未知错误: {0}'.format(str(e))) + '\r\n')
            return True

        if isinstance(result, dict):
            s = u"""
 \t\t主机名     : {name}\r
 \t\t主机ip     : {ip}\r
 \t\t主机类型   : {host_type}\r
 \t\tcpu        : {cpu}核\r
 \t\t内存       : {memory}\r
 \t\t硬盘       : {disk}\r
 \t\t序列号     : {sn}\r
 \t\t操作系统   : {os}\r
 \t\t内核       : {kernel}\r
 \t\t上线时间   : {purchase_at}\r
 \t\tidc机房    : {idc}\r
 \t\t开发负责人 : {rd}\r
 \t\t测试负责人 : {ep}\r
 \t\t运维负责人 : {op}\r\n
            """
            s = s.format(**result)
            channel.sendall(get_colour(s, colour='green') + '\r')
        else:
            channel.sendall(get_colour(result + '\r\n'))

    @staticmethod
    def pssh(jumper, terminal, channel, command):
        """
        用法例子: pssh jumper-service uptime
        :param jumper:   用户信息等
        :param command:  uptime
        :return:
        """
        FAILURE_CONNECT = "\033[0;36m[\033[0m{0}\033[0;36m]\033[0m {1} \033[0;31m[FAILURE]\033[0m {2} {3}, 连接主机异常"
        FAILURE_EXIT = "\033[0;36m[\033[0m{0}\033[0;36m]\033[0m {1} \033[0;31m[FAILURE]\033[0m {2} {3}"
        SUCCESS = "\033[0;36m[\033[0m{0}\033[0;36m]\033[0m {1} \033[0;34m[SUCCESS]\033[0m {2} {3}"
        op = PsshOptions(command)
        if not op.status:
            channel.sendall(get_colour(op.help, colour='green'))
            channel.sendall(terminal.user_ps1)
            return True
        password = config['uuid']
        username = jumper.user_name
        port = int(config['ssh_backend_port'])
        hosts = op.info['hosts']
        if hosts is None:
            channel.sendall(get_colour(u'哎哟, 应用查询接口出现问题, 重试一下, 或者联系跳板机管理员!\r\n'))
            channel.sendall(terminal.user_ps1)
            logging.error(u'哎哟, 应用查询接口出现问题, 重试一下, 或者联系跳板机管理员!, 错误命令:{0}'.format(command))
            return True
        if len(hosts) == 0:
            if command.startswith('pssh'):
                channel.sendall(get_colour(u'找不到应用:{0}, 拼写错误? pssh查看帮助\r\n'.format(op.app_name), colour='red'))
            else:
                channel.sendall(get_colour(u'找不到应用:{0}, 拼写错误? plog查看帮助\r\n'.format(op.app_name), colour='red'))
            channel.sendall(terminal.user_ps1)
            return True
        commands = op.info['command']

        terminal.pause = False
        t2 = Thread(target=terminal.get_interruption,
                    args=(channel, jumper, 'pssh'))
        t2.setDaemon(True)
        t2.start()
        i = 1
        for h in hosts:
            hostname, ip = h.split(':')
            if terminal.pause is True:
                break
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                logging.info('plog|pssh 连接主机端口 {0}, 尝试端口 22'.format(hostname))
                ssh.connect(ip, port, username, password, timeout=int(config['pssh_timout']))
            except:
                if port != 58422 and alive_port(ip, 58422):
                    logging.info('plog|pssh 连接主机端口 {0} 失败, 尝试端口 58422'.format(port))
                    try:
                        ssh.connect(ip, 58422, username, password, timeout=int(config['pssh_timout']))
                    except:
                        channel.sendall(u'{0}.\r\n'.format(FAILURE_CONNECT.format(i, time.strftime('%H:%M:%S'), hostname, ip)))
                        i += 1
                        continue
                else:
                    channel.sendall(u'{0}.\r\n'.format(FAILURE_CONNECT.format(i, time.strftime('%H:%M:%S'), hostname, ip)))
                    i += 1
                    continue
            _, stdout, stderr = ssh.exec_command(commands)
            code = stdout.channel.recv_exit_status()
            if code != 0:
                output = stderr.readlines()
                if len(output) == 0:
                    channel.sendall(FAILURE_EXIT.format(i, time.strftime('%H:%M:%S'), hostname, ip) + '\033[0;31m 命令返回结果为空\033[0m\r\n')
                else:
                    channel.sendall(FAILURE_EXIT.format(i, time.strftime('%H:%M:%S'), hostname, ip) + '\r\n')
                for x in output:
                    channel.sendall(x + '\r')
                    channel.sendall('\r')
            else:
                channel.sendall(SUCCESS.format(i, time.strftime('%H:%M:%S'), hostname, ip) + '\r\n')
                for x in stdout.readlines():
                    channel.sendall(x + '\r')
                channel.sendall('\r')
            i += 1
        if terminal.pause is True:
            channel.sendall('^C\r\n')
        terminal.password_send.sendall('\\')
        terminal.pause = True
        channel.sendall(terminal.user_ps1)
        return True

    @staticmethod
    def ping(terminal, command, channel, jumper):
        terminal.pause = False
        usage = """
    简化版ping，仅仅支持如下用法，多余参数不支持\r

    ping hostname|ip\r
    例子: ping jumper-web02.nh\r
    例子: ping 127.0.0.1\r\n\n"""
        cut_cmd = command.strip().split()
        if len(cut_cmd) == 2:
            host = cut_cmd[1]
            ip_reg = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
            dns_reg = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
            if not re.match(ip_reg, host) and not re.match(dns_reg, host):
                channel.sendall(get_colour(u'非规范主机名! 请检查拼写后再使用!\r\n', colour='red'))
                channel.sendall(terminal.user_ps1)
                return
            _stderr, _stdout = subprocess.PIPE, subprocess.STDOUT
            p = subprocess.Popen("ping {0}".format(host), shell=True, stdout=_stderr, stderr=_stdout)
            command_pids['channel_{0}'.format(channel.get_id())].append(p.pid)
            kwargs = dict(proxy_channel=channel, jumper=jumper, popen=p)
            AsyncThread(target=terminal.get_interruption, **kwargs)
            # 用于检查子进程是否已经结束
            return_code = p.poll()
            while return_code is None:
                channel.sendall(u'{0}\r\n'.format(p.stdout.readline().strip()))
                return_code = p.poll()
            terminal.password_send.sendall('\\')
            terminal.pause = True
        else:
            channel.sendall(get_colour(usage, colour='green'))
        channel.sendall(terminal.user_ps1)

    @staticmethod
    def kinit(status, terminal, channel, user_info, proxy_server):
        count = 0
        while True:
            if count == 3:
                channel.sendall(get_colour(u'输入错误密码3次, 不给你恢复会话!\r\n'))
                channel.sendall(terminal.user_ps1)
                break
            password = terminal.get_password(status, channel, u'请输入密码: ')
            if not password:
                channel.sendall(get_colour(u'密码不允许为空\r\n'))
                count += 1
            elif password == '^C':
                channel.sendall('^C\r\n')
                channel.sendall(terminal.user_ps1)
                break
            elif Password.check_password(user_info, password):
                connection_info = dict(
                        type='login_info',
                        pid=os.getpid(),
                        uuid=config['uuid'],
                        user_id=proxy_server.user_info['uid'],
                        login_name=proxy_server.user_info['login_name'],
                        login_time=proxy_server.user_info['login_time'],
                        name=proxy_server.user_info['name'],
                        server_name=config['server_name'],
                        client_ip=proxy_server.client_ip,
                        client_port=proxy_server.client_port,
                )
                result = Async.add_uuid(connection_info, proxy_server.user_info['source'])
                if result:
                    channel.sendall(get_colour(u'密码正确, 会话已恢复!\r\n', colour='blue'))
                else:
                    channel.sendall(get_colour(u'会话未正常恢复, 请联系管理员!\r\n'))
                channel.sendall(terminal.user_ps1)
                break
            else:
                channel.sendall(get_colour(u'密码错误, 请重新输入!\r\n'))
                count += 1

    @staticmethod
    def history(command, channel, terminal_control):
        usage = """usage:\r
        history 查看历史命令\r
        history -c 清空历史记录\r\n"""
        if command.strip() == 'history':
            length = len(commands_list)
            for index, command in enumerate(commands_list):
                single_record = '%4d  ' % (length-index) + command.values()[0] + '   ' + command.keys()[0] + '\r\n'
                channel.sendall(get_colour(single_record, colour='green'))
        else:
            temp = command.split()
            if 'history -c' == ' '.join(temp):
                del commands_list[:]
                terminal_control.command_list = []
                terminal_control.command_index = 0
                config['task'].add_task(Async.put_command_history, config['user_name'], [])
            else:
                channel.sendall(get_colour(usage))

    @staticmethod
    def ping_close(channel_id):
        if channel_id is not None:
            for pid in command_pids['channel_{0}'.format(channel_id)]:
                try:
                    os.kill(pid, 15)
                except Exception as e:
                    logging.info(u'结束 ping 进程失败: {0} {1}'.format(e, pid))
        else:
            for channel in command_pids.keys():
                for pid in command_pids[channel]:
                    try:
                        os.kill(pid, 15)
                    except Exception as e:
                        logging.info(u'结束 ping 进程失败: {0} {1}'.format(e, pid))
