# -*- coding: utf-8 -*-

from datetime import datetime
from app.lib.database import db, Model, Column


class Host(Model):
    """ 主机列表 """
    __table_name__ = 'host'
    id = Column(db.Integer, primary_key=True)
    corp = Column(db.String(128))
    owt = Column(db.String(64), index=True)
    pdl = Column(db.String(64), index=True)
    srv = Column(db.String(64), index=True)
    cluster = Column(db.String(256))
    host_ip = Column(db.String(64), nullable=False, index=True)
    host_name = Column(db.String(128), nullable=False, index=True)
    host_fqdn = Column(db.String(128), nullable=False, index=True)
    host_port = Column(db.Integer, nullable=False, default=22)
    host_type = Column(db.String(64), nullable=False, default='kvm')
    login_type = Column(db.String(32), nullable=False, default='ssh')


class LoginHistory(Model):
    """ 登录历史 """
    __table_name__ = 'login_history'
    id = Column(db.Integer, primary_key=True)
    jumper_name = Column(db.String(128), index=True)
    host_type = Column(db.String(64), nullable=False, index=True, default='kvm')
    host_ip = Column(db.String(64), index=True)
    host_name = Column(db.String(128), nullable=False, index=True)
    host_port = Column(db.Integer, nullable=False, default=22)
    remote_ip = Column(db.String(64), nullable=False)
    remote_port = Column(db.Integer, nullable=False)
    login_name = Column(db.String(64), index=True)
    user_name = Column(db.String(32), nullable=False, index=True)
    user_uid = Column(db.Integer, nullable=False)
    login_type = Column(db.String(32), nullable=False, default='ssh')
    login_uuid = Column(db.String(64), nullable=False)
    login_time = Column(db.DateTime, default=datetime.now, index=True)
    logout_time = Column(db.DateTime, index=True)
    channel_id = Column(db.Integer, nullable=False, default=0)
    session_uuid = Column(db.String(64), nullable=False)
    recorder = Column(db.PickleType, default=list())


class CommandHistory(Model):
    """ 历史命令 """
    __table_name__ = 'command_history'
    id = Column(db.Integer, primary_key=True)
    user_name = Column(db.String(32), nullable=False, index=True)
    login_name = Column(db.String(32), nullable=False, index=True)
    exec_time = Column(db.DateTime)
    host_ip = Column(db.String(64), index=True)
    host_name = Column(db.String(64), nullable=False, index=True)
    command = Column(db.Text, nullable=False)
    danger = Column(db.Integer, default=0)
    login_uuid = Column(db.String(64), nullable=False)
    session_uuid = Column(db.String(64), nullable=False)


class Auth(Model):
    """ 授权表 """
    __table_name__ = 'auth'
    id = Column(db.Integer, primary_key=True)
    role = Column(db.String(32), nullable=False, default='user', index=True)
    role_id = Column(db.Integer, nullable=False, index=True)
    auth_type = Column(db.String(32), default='login')
    label = Column(db.String(128), nullable=False, index=True)
    label_key = Column(db.String(128), nullable=False, index=True)
    life_cycle = Column(db.DateTime, index=True)
    protocol = Column(db.String(16), default='ssh')


class User(Model):
    """ 用户列表 """
    __table_name__ = 'user'
    uid = Column(db.Integer, primary_key=True)
    gid = Column(db.Integer)
    number = Column(db.Integer)
    name = Column(db.String(64), nullable=False)
    login_name = Column(db.String(64), nullable=False, index=True)
    source = Column(db.String(16))
    email = Column(db.String(512), nullable=False)
    mobile = Column(db.BIGINT)
    organization = Column(db.String(1024))
    type = Column(db.String(32), default='guest', index=True)
    role = Column(db.String(32), default='rd', index=True)
    enable = Column(db.Integer, default=0, index=True)
    register_time = Column(db.DateTime, default=datetime.now)
    login_time = Column(db.DateTime, default=datetime.now)
    password = Column(db.String(128))
    password_mtime = Column(db.DateTime, default=datetime.now)
    old_password_dict = Column(db.PickleType, default=dict())
    salt = Column(db.String(64))
    home_dir = Column(db.String(32))
    shell = Column(db.String(32), default='/bin/bash')
    key = Column(db.String(4096))
    public_key = Column(db.String(4096))
    login_type = Column(db.String(32), default='default')
    birthday = Column(db.DateTime)
    desc = Column(db.Text)


class Group(Model):
    """ 用户组 """
    __table_name__ = 'group'
    gid = Column(db.Integer, primary_key=True)
    group_name = Column(db.String(128), nullable=False)
    type = Column(db.String(16), default='auth', index=True)
    desc = Column(db.Text)


class Mapper(Model):
    """ 用户和组多对多中间表
    """
    __table_name__ = 'mapper'
    uid = Column(db.Integer, primary_key=True)
    gid = Column(db.Integer, primary_key=True)
    type = Column(db.String(16), default='auth', index=True)
    user_name = Column(db.String(64), nullable=False, index=True)
    group_name = Column(db.String(128), nullable=False, index=True)


class Sudo(Model):
    """
    用户sudo记录表
    """
    __table_name__ = 'sudo'
    id = Column(db.Integer, primary_key=True)
    role = Column(db.String(32), nullable=False)
    role_name = Column(db.String(128), nullable=False)
    hosts = Column(db.String(1024), default='ALL')
    users = Column(db.String(1024), default='ALL')
    password_option = Column(db.String(16), default='NOPASSWD')
    commands = Column(db.String(1024), default='ALL')
    label = Column(db.String(64), nullable=False)
    label_key = Column(db.String(128), nullable=False)
    life_cycle = Column(db.DateTime)


class Session(Model):
    """
    用户session记录表
    """
    __table_name__ = 'session'
    id = Column(db.Integer, primary_key=True)
    ttl = Column(db.Integer)
    name = Column(db.String(64))
    login_name = Column(db.String(64), nullable=False, index=True)
    server_name = Column(db.String(128), nullable=False, index=True)
    uuid = Column(db.String(64), nullable=False)
    login_time = Column(db.DateTime)
    logout_time = Column(db.DateTime)
    user_id = Column(db.Integer, nullable=False, index=True)
    pid = Column(db.Integer, nullable=False)
    client_port = Column(db.Integer, nullable=False)
    client_ip = Column(db.String(32), nullable=False, index=True)
