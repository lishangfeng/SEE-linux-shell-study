# -*- coding:utf-8 -*-

# 应用名
app_name = 'jumper-service'

# 会根据此环境读取对应的lion配置
app_env = 'product'

# 工作模式 process: 进程模式(推荐使用), thread: 线程模式
server_type = 'process'

# pid文件
pid_file = '/var/run/{0}.pid'.format(app_name)

# 日志路径
log_file = '/data/applogs/{0}/logs/jumper.log'.format(app_name)

# 日志级别 [DEBUG, INFO, WARNING, ERROR]
log_level = 'DEBUG'

# 每份日志大小, 30M
log_size = 1024 * 1024 * 100

# 切割后日志保存份数
log_rotate_backup_count = 200

# 密码过期时间, 60天
password_ttl = 60

# 伪终端保持回话功能, 主动向client每10分钟发送一个心跳
ssh_keep_alive = 600

# 伪终端未登录后端机器最长空闲时间 25小时
vacant_timeout = 25 * 60 * 60

# 用户输入密码错误超过6次锁定时间, 单位为秒, 30分钟
lock_user_ttl = 30 * 60

# pssh 连接主机超时时间
pssh_timout = 5

# 连接后端默认端口
ssh_backend_port = 22

# 监听端口
ssh_server_port = 2200

# 监听ip地址
ssh_server_ip = '0.0.0.0'

# 开启二次验证
dynamic_password = True

# 终端新闻发布, 默认不设置
terminal_news = ''

# 生日提醒
birthday_news = u'在这个特殊的日子里，你还默默地奋斗在一线，Jumper祝您生日快乐!'
midnight_birthday_news = u'夜已深了，Jumper祝您生日快乐，处理完事情快去休息吧！'

# 降级提醒
degrade_news = u'服务已降级！服务已降级！服务已降级！登录无需输入大象动态码!'

# 温馨提醒
ai_news = dict(deep_night=u'夜已深了，为迎接美好的一天，请您处理完紧急事情后就去休息吧!')

# 登录时发送大象消息验证码
dx_code = True

# 允许key登录的用户
admin_role = ['op', 'sre']

# Administrator 收发大象报警
# admin_user = 'alex.wan@dianping.com,kui.xu@dianping.com'
admin_user = 'alex.wan@dianping.com'

# 危险命令发送
warning_user = 'alex.wan@dianping.com'
# hr系统
ops_auth = ''

# 大象动态key
app_id = ''
sha_key = ''
client_ua = ''
google_auth_api = ''
network_interface = 'eth0'

# http api
api_token = ''
api_domain = ''
takecare = 'https://jumper-takecare.sankuai.com/api/queue'
takecare_token = 'changeme'

# 历史命令记录条数
history_size = 500

# mss 服务端地址
mss_server = 'mss.vip.sankuai.com'

# mss_key 证书
mss_access = '733474cc8a424b7a87ac7338109249bd'

# mss_secret 密钥
mss_secret = '92a39ae971a94ff98dbdba5263b92d9e'

# 单个会话录像切割份数
recorder_number = 20

# 累计多少个命令push
command_push_count = 3

# 危险命令过滤条件
danger_regular = [
    '(\s*)rm\s+?/\s+?-rf(\s*)',
    '(\s*)rm\s+?-rf\s+?/(\s*)',
    '(\s*)history\s+?-c(\s*)',
    '(\s*)chmod\s+?0?777\s+?/',
    '(\s*)createrepo\s+?-d\s+?--update(\s*)'
]

# 健康检查黑名单
health_check = [
    '10.12.4.2',
    '10.12.4.66',
    '10.32.4.66',
    '10.32.4.74',
    '10.32.4.90',
    '10.32.10.130',
    '10.32.254.2',
    '10.32.254.130',
    '10.69.3.2',
    '10.69.4.2',
    '10.69.5.2',
    '10.69.6.2',
    '10.16.3.2',
    '10.16.3.130',
    '10.4.12.2',
    '10.4.13.2',
    '10.4.4.98',
    '10.4.4.106'
]

# 机房idc
idc = {
    "xh": u"徐汇",
    "gq": u"桂桥",
    "dba": u"数北A",
    "sdyd": u"山东移动",
    "cd": u"成都",
    "tencent": u"腾讯",
    "cq": u"次渠",
    "zw": u"中卫",
    "gh": u"光环",
    "nh": u"南汇",
    "sdlt": u"山东联通",
    "nj": u"南京",
    "rz": u"润泽",
    "wj": u"望京",
    "yf": u"永丰",
    "yy": u"易园",
    "yz": u"扬州",
    "dx": u"大兴",
    "bs": u"宝山",
    "yp": u"月浦",
    "sjz": u"石家庄",
    "sb": u"市北",
    "kx": u"天津"
}
