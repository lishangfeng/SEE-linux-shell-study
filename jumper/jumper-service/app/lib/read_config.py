#!/bin/env python
# -*- coding:utf-8 -*-

import os
import imp
import linecache
from werkzeug.utils import import_string

from app.lib.lion import Lion


class ReadConfig:
    def __init__(self):
        self.lion = True
        self.app_env = 'product'
        self.config = dict()
        self.root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.main()

    def main(self):
        """ 初始化配置 """
        conf = import_string('config')
        conf_instance = self.from_file('instance/config.py')

        # 读取app_env
        if hasattr(conf_instance, 'app_env'):
            self.app_env = getattr(conf_instance, 'app_env')
        elif os.path.exists('/data/webapps/appenv'):
            try:
                for line in open('/data/webapps/appenv').xreadlines():
                    if 'deployenv=' in line:
                        self.app_env = line.split('deployenv=')[1].strip()
                        break
            except IOError:
                pass
        elif hasattr(conf, 'app_env'):
            self.app_env = getattr(conf, 'app_env')

        # 读取lion开关
        if hasattr(conf_instance, 'lion'):
            self.lion = getattr(conf_instance, 'lion')
        elif hasattr(conf, 'lion'):
            self.lion = getattr(conf, 'lion')
        self.config['lion'] = self.lion
        self.config['lion_key'] = conf.app_name

        # 设置配置
        self.from_object(conf)
        if self.lion:
            self.config.update(Lion(app_name=self.config['lion_key'], app_env=self.app_env).config)
        self.from_object(conf_instance)
        self.config['app_env'] = self.app_env

    def from_object(self, obj):
        """ 设置配置 """
        for key in dir(obj):
            if not key.startswith('__'):
                self.config[key] = getattr(obj, key)

    def from_file(self, filename):
        """ 读取配置文件 """
        filename = os.path.join(self.root_path, filename)
        d = imp.new_module('config')
        d.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
        except IOError:
            return object
        return d
