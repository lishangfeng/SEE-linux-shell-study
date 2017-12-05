# -*- coding: utf-8 -*-

import os

APP_NAME = 'jumper-web'
basedir = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.join(basedir, 'data')
SECRET_KEY = 'W.k~[\x9c:$\xfb\x93fP\xb6\x07\xa1\x16\xc3\xb1\xec\x17KL\x08_]'

# lion开关, 默认开启
LION = True

# URL前缀
URL_PREFIX = '/api'

# debug模式默认关闭
DEBUG = False

# 环境[qa=beta, prelease=ppe, product=生产], 用于读取lion配置项, 以及开启db后台等
APP_ENV = 'product'

# 管理员
ADMIN_ROLE = ['op', 'sa', 'sre', 'srd']

# 金融组会话超时时间, 15分钟
FINANCE_EXPIRE_TIME = 15 * 60

# 日志级别 [DEBUG, INFO, WARNING, ERROR]
LOG_LEVEL = 'DEBUG'

# 日志文件路径
APP_LOG = '/data/applogs/{0}/logs/app.log'.format(APP_NAME)

# nss-cache内存缓存
NSS_USER = None
NSS_GROUP = None
NSS_VERSION = None

# /nss/cache 停止同步账号开关, [on|off]
NSS_SWITCH = 'off'

# 上海db鉴权pdl
AUTH_PDL = ["jgdb", "zudb", "pltdb", "addb", "zsdb", "poi-info", "trvdb", "epdb", "dcdb", "kfdbcc", "wmdb", "mydb", "wsh"]

# 维护的 nss 缓存增量版本数量, 用于客户端增量更新
NSS_CACHE_VERSION = 50

# Nss 本地缓存目录
NSS_CACHE_LOCAL_DIR = '/dev/shm'

# 每份日志大小, 100M
LOG_SIZE = 1024 * 1024 * 100

# 切割后日志保存份数
LOG_ROTATE_BACKUP_COUNT = 15

# 分页大小
PAGE_SIZE = 25

# api授权
API_TOKEN = [dict(key='yTe<9+={}]:m_aHY', desc=u'服务树', type='root')]

# 特殊session会话组, expire为超时时间, 单位分钟
SESSION_EXPIRE = [dict(organization=u'集团/金融服务平台', expire=15)]

# dp sudoers
SUDO_GROUP = ['dp_op', 'sudo_sankuai.stree.meituan.sre']

# dp minor groups
MINOR_PRIVILEGE = "/usr/bin/svc"

# falcon 监控主机
ENDPOINT = "jumper-service01.gq"
COUNTER_LIST = ['dp_user_online', 'mt_user_online', 'backend_online', 'dp_session_online', 'mt_session_online']

# 读取用户信息api
OPS_AUTH = 'https://ops-auth.sankuai.com/userService/getByAd?ad={0}'

# wiki使用手册
WIKI = 'http://wiki.sankuai.com/pages/viewpage.action?pageId=624539419'

# sso认证
SSO_AUTH = True
CALL_BACK = False
# CAS_AFTER_LOGIN = '/api/user/register'
CAS_AFTER_LOGIN = '/'
CAS_SERVER = 'https://sso.dper.com'
CAS_LOGIN_ROUTE = '/login'
CAS_LOGOUT_ROUTE = '/logout'
CAS_VALIDATE_ROUTE = '/serviceValidate'

# redis 配置
MAX_CONNECTIONS = 50  # connection pool max size
# dp 用于上海用户写session
# default  用于北京写session, 同时默认用于nss写缓存
# readonly 用于nss缓存读取, 和default配置主从, default默认也会加入readonly组
REDIS_POOL = dict(
    dp='redis://root:123456@127.0.0.1',
    default='redis://root:123456@127.0.0.1',
    readonly=['redis://root:123456@127.0.0.1']
)

# MySQL配置
SQLALCHEMY_ECHO = False         # debug mode will be useful
SQLALCHEMY_POOL_SIZE = 16       # default 5 usually
SQLALCHEMY_POOL_TIMEOUT = 10    # default 10s
SQLALCHEMY_MAX_OVERFLOW = 10    # default will not allow overflow
SQLALCHEMY_POOL_RECYCLE = 7200  # session engine reconnect timeout
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = 'mysql://account:passwd@127.0.0.1/jumper'

# UPLOADED_PATH = '/tmp'

# Job admin
# admin_user = 'alex.wan@dianping.com,kui.xu@dianping.com'

JOB_ADMIN = 'alex.wan@dianping.com'
