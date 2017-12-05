# -*- coding:utf-8 -*-

import re
from getopt import GetoptError
from getopt import gnu_getopt

from app.lib.async import Async
from app.lib.utils import get_colour

from app.ssh_server.init import config


class SshOptions:
    def __init__(self, args):
        self.args = [i for i in args.split(' ') if i and i != 'ssh']
        self.info = dict()
        self.status = False
        self.help = u"""
    用法:\r
    ssh username@hostname|IP [-p port]\r
    ssh hostname|IP [-l user] [-p port]\r

    例子0: ssh 192.168.0.1 (以当前用户名登录目标机器)\r
    例子1: ssh jumper-service01.gq (以当前用户名登录目标机器)\r
    例子2: ssh root@dx-sre-jumper-service01 (以root账号登录目标机器)\r
    例子2: ssh dx-sre-jumper-service01 -l sankuai (以sankuai账号登录目标机器)\r
    例子3: ssh jumper-service01.gq -p 58422 (目标机器ssh端口为58422)\r\n\n"""
        self.main()

    def main(self):
        if not self.args:
            return False
        self.get_options()
        if self.info.get('host_port'):
            try:
                self.info['host_port'] = int(self.info['host_port'])
            except ValueError:
                self.help = u'端口输入错误, 端口只能是整数!\r\n'
                return False
        else:
            self.info['host_port'] = int(config.get('ssh_backend_port'))

        if self.info.get('host_name'):
            self.status = True

    def get_options(self):
        # -l指定的用户名优先级在标准ssh下高于主机前面的@用户名
        # 例如 ssh root@jumper.dper.com -lalex.wan, 最终确定的用户是alex.wan
        try:
            options, args = gnu_getopt(self.args, 'l:p:')
        except GetoptError:
            self.help = u'命令中含有不支持的参数, 输入ssh查看使用方法!\r\n'
            self.status = False
            return
        for i in args:
            if i.find('@') > 0:
                t = i.split('@')
                if len(t) == 2:
                    self.info['user_name'], self.info['host_name'] = t
                    break
                elif len(t) > 2:
                    self.info['host_name'] = t[-1]
                    self.info['user_name'] = '@'.join(t[:-1])
                    break
        for k, v in options:
            if k == '-l' and v:
                self.info['user_name'] = v
            elif k == '-p' and v:
                self.info['host_port'] = v

        if not self.info.get('host_name'):
            if not args:
                self.help = u'命令缺少主机, 输入ssh查看使用方法!\r\n'
                self.status = False
                return
            self.info['host_name'] = args[0]


class PsshOptions:
    def __init__(self, args):
        self.info = dict()
        self.app_name = ''
        self.args = args.strip()
        self.status = False
        self.help = ''
        self.main()

    def main(self):
        if not self.args:
            return False
        if self.args.split()[0] == 'pssh':
            self.get_pssh_option()
        elif self.args.split()[0] == 'plog':
            self.get_plog_option()
        else:
            self.help = get_colour('''命令 {0} 不存在, 键入 H 查看帮助信息\r\n'''.format(self.args.split()[0]))

    def get_pssh_option(self):
        # 获取hosts并且分析
        if len(self.args.split()) >= 3:
            self.status = True
            self.app_name = project = self.args.split()[1]
            self.info['hosts'] = Async.cmdb(project=project)
        else:
            self.help = u"""\r
    机器在上海申请\r
    用法: pssh app_name command\r
    例子: pssh shop-web uptime\r
    例子: pssh shop-web /sbin/ifconfig|awk '{print $1}'\r
    命令只在线上主机执行, ppe,beta机器不会被执行\r

    机器在北京申请\r
    pssh owt.pdl.srv|owt.pdl.srv.cluster command (cluster可选, 默认执行prod环境)\r
    例子: pssh sre.jumper.service uptime (仅在prod环境机器执行)\r
    例子: pssh sre.jumper.service.staging uptime (仅执行staging环境机器)\r\n\n"""
            return False

        # 获取command
        temp = self.args.split()
        del temp[0]
        del temp[0]
        commands = ' '.join(temp)
        if len(commands) > 2 and (commands[0] == commands[-1] == "'" or commands[0] == commands[-1] == '"'):
            self.info['command'] = commands[1:-1]
        else:
            self.info['command'] = commands

    def get_plog_option(self):
        # 获取hosts并且分析
        if len(self.args.split()) >= 4 and (re.match('(^\'.*\'$)|(\".*\"$)', self.args.split()[-1])
                                       or re.match(r'^(\'|\")?\d{4}-\d{2}-\d{2}(\'|\")?$', self.args.split()[-1])):
            if not re.match('(^\'\d{4}-\d{2}-\d{2}\'$)|(^\"\d{4}-\d{2}-\d{2}\"$)|(^\d{4}-\d{2}-\d{2}$)',
                            self.args.split()[-1]):
                self.help = u'''请输入标准日期格式: "Year-Month-Day"\r\n''' + get_colour(
    u'''例子: plog shop-web "ERROR" "2017-01-01"\r\n''', colour='blue')
                return False
            self.status = True
            self.app_name = project = self.args.split()[1]
            rule_index = self.args.find(self.args.split()[2])
            rule_end = self.args.find(self.args.split()[-1])
            grep_rule = self.args[rule_index:rule_end].strip()
            date = self.args.split()[-1]
            self.info['hosts'] = Async.cmdb(project=project)
            self.info['command'] = u'grep {0} /data/applogs/{1}/logs/app.log.{2}'.format(grep_rule, project, date)
        elif len(self.args.split()) >= 3:
            self.status = True
            self.app_name = project = self.args.split()[1]
            rule_index = self.args.find(self.args.split()[2])
            grep_rule = self.args[rule_index:].strip()
            self.info['hosts'] = Async.cmdb(project=project)
            self.info['command'] = u'grep {0} /data/applogs/{1}/logs/app.log'.format(grep_rule, project)
        else:
            self.help = u"""\r
    此命令仅限查询上海机器标准日志文件(/data/applogs/{app_name}/logs/app.log)\r
    北京机器日志存放暂无固定名，可移步pssh替代方案\r\n
    usage: plog app_name grep_rule Year-Month-Day\r

    例子: plog shop-web "ERROR"\r
    相当于 ==> pssh shop-web grep "ERROR" /data/applogs/shop-web/logs/app.log\r

    例子: plog shop-web "ERROR" "2017-01-01"\r
    相当于 ==> pssh shop-web grep "ERROR" /data/applogs/shop-web/logs/app.log.2017-01-01\r
    只查询线上日志, ppe,beta机器日志不会查询\r\n\n"""
            return False
