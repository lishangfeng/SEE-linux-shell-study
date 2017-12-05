#!/bin/env python
# -*- coding:utf-8 -*-

import pkgutil
from uuid import uuid4
from flask import Blueprint, g
from flask import session, request, redirect, url_for


from app.sso import CAS
from app.lib.app_logger import AppLogger
from app.lib.error_define import *


class MakeApp:
    def __init__(self, flask_app):
        self.app = flask_app
        self.profile = Blueprint('api', __name__)

    def init_all(self, extensions=None, views=None):
        self.init_config()
        self.init_log()
        self.init_before()
        self.init_after()
        self.init_sso()
        self.init_error_handler()
        self.load_module_dynamic(extensions)
        self.load_module_dynamic(views, _type='view')

    def init_config(self):
        """
        初始化 flask 配置
        优先级: config.py -> lion -> instance/config.py
        """
        self.app.config.from_object('config')
        self.app.config.from_pyfile('config.py')

    def init_log(self):
        AppLogger(self.app)

    def init_sso(self):
        if self.app.config.get('SSO_AUTH'):
            CAS(self.app)

    def init_before(self):
        @self.app.before_request
        def before_request():
            g.uuid = str(uuid4()).split('-')[-1]
            token = request.headers.get('Authorization', None)
            if token and [i for i in self.app.config.get('API_TOKEN', dict()) if i['key'] == token]:
                g.token = [i for i in self.app.config.get('API_TOKEN', []) if i['key'] == token][0]
                g.sso = dict(name=u'Token账号', login_name='Authorization', number=1001)
                return
            elif session.get('CAS_USERNAME'):
                return
            elif request.path.startswith('/api/') or request.path.startswith('/static'):
                return
            elif request.path in ['/login', '/logout']:
                return
            elif not self.app.config.get('SSO_AUTH'):
                g.sso = dict(name=u'测试账号', login_name='test', number=1001)
                return
            return redirect(url_for('cas.login', _external=True))

    def init_after(self):
        @self.app.after_request
        def after_request():
            pass

    def init_error_handler(self):
        @self.app.errorhandler(ValidationError)
        def handle_validation(error):
            return res(code=203, msg=error.msg)

        @self.app.errorhandler(SupportError)
        def handle_support(error):
            return res(code=204, msg=error.msg)

        @self.app.errorhandler(PermissionError)
        def handle_permission(error):
            return res(code=205, msg=error.msg)

        @self.app.errorhandler(RedisError)
        def handle_redis(error):
            return res(code=206, msg=error.msg)

        @self.app.errorhandler(SQLAlchemyError)
        def handle_sqlalchemy(error):
            return res(code=207, msg=error.msg)

    def load_module_dynamic(self, extensions, _type='extension'):
        """ 动态加载 flask扩展 以及 视图函数 """
        module_priority_chain = getattr(extensions, 'module_priority_chain', [])
        module_blacklist = getattr(extensions, 'module_blacklist', [])
        init_mod_list = []

        for name in module_priority_chain:
            try:
                _module = __import__('{0}.{1}'.format(extensions.__name__, name), fromlist=[''])
            except ImportError:
                continue
            init_mod_list.append(_module)

        for _, name, _ in pkgutil.iter_modules(extensions.__path__):
            mod_name = '{0}.{1}'.format(extensions.__name__, name)
            if mod_name.split('.')[-1] in module_priority_chain + module_blacklist:
                continue
            else:
                _module = __import__('{0}.{1}'.format(extensions.__name__, name), fromlist=[''])
            init_mod_list.append(_module)

        for _module in init_mod_list:
            if _type == 'view':
                print u'loading {0:10}: {1:35} =>    register'.format(_type, _module.__name__)
                continue

            if not hasattr(_module, 'extension'):
                print u'loading {0:10}: {1:35} =>    ignore'.format(_type, _module.__name__)
            else:
                getattr(_module.extension, 'init_app')(self.app)
                print u'loading {0:10}: {1:35} =>    register'.format(_type, _module.__name__)

        if _type == 'view':
            self.app.register_blueprint(self.profile, url_prefix=self.app.config.get('URL_PREFIX', '/api'))
