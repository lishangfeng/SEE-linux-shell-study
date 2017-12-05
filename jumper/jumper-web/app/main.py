# -*- coding: utf-8 -*-

from flask import Flask

from app import extensions, views
from app.make_app import MakeApp


app = Flask(__name__, instance_relative_config=True)
with app.app_context():
    init_app = MakeApp(app)
    profile = init_app.profile
    # init_app.init_all(extensions, views)

    init_app.init_config()
    init_app.init_log()
    init_app.init_before()
    init_app.init_sso()
    init_app.init_error_handler()
    init_app.load_module_dynamic(extensions)
    init_app.load_module_dynamic(views, _type='view')
