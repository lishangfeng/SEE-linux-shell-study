#!/bin/env python
# -*- coding:utf-8 -*-

import json
from flask import Flask
from functools import wraps
from flask.app import request
from werkzeug.wrappers import Response

from app.main import profile
from app.lib.utlis import json_loads
from app.lib.permission import Permission
from app.lib.error_define import ValidationError, res
from app.lib.validation_request_data import PreProcessorChain
from app.lib.validation_request_data import ValidationRequestData


class ViewDecorator:
    """获取请求数据, 以及一些列预处理
    """
    def __init__(self, rule, methods=None, args=True, response=True):
        self.rule = rule
        self.args = args
        self.response = response
        self.methods = (methods or ['GET'])

        self.name = None
        self.result = False
        self.request_data = dict()

    def __call__(self, view_function):
        self.name = view_function.__name__

        @profile.route(rule=self.rule, methods=self.methods)
        @wraps(view_function)
        def wrapped(**kwargs):
            self.request_data = dict(post=dict(), get=dict())
            self.request_data['get'].update(kwargs)
            self.pre_process()
            if self.args:
                self.result = view_function(self.request_data)
            else:
                self.result = view_function()
            if self.response:
                return self.post_process()
            else:
                return self.result or ' '
        return wrapped

    def pre_process(self):
        # # 权限控制
        Permission.filter(self.name)
        # 获取请求数据
        self.get_http_data()
        # 验证数据格式
        ValidationRequestData.process(self.request_data, self.name)
        # 验证数据逻辑
        data = PreProcessorChain.process(process_type=self.name, request_data=self.request_data)
        self.request_data.update(data) if data else False

    def get_http_data(self):
        self.request_data['get'].update(request.args.to_dict())
        try:
            if request.data:
                self.request_data['post'] = json.loads(request.data)
            elif request.method == 'POST':
                raise ValidationError(u'未提交任何数据')
        except ValueError:
            raise ValidationError(u'POST提交数据不是json格式')
        if self.request_data:
            self.request_data = json_loads(self.request_data)

    def post_process(self):
        if not self.result:
            return res()
        elif isinstance(self.result, Flask.response_class):
            return self.result
        elif isinstance(self.result, Response):
            return self.result
        else:
            return res(result=self.result)
