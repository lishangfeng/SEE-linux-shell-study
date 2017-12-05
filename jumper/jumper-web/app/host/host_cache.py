# -*- coding: utf-8 -*-

from threading import Thread

from app.main import app
from app.models import Host
from app.lib.app_redis import Rds
from app.lib.error_define import RedisExceptionError


class HostCache(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.data = data
        self.daemon = True

    def run(self):
        with app.app_context():
            self.process()

    def process(self):
        _data = self.data

        result = Host.get_by(first=True, **_data)
        if result:
            Rds.router().set_host(result)
        else:
            Rds.router().del_host(_data['host_ip'])

    @staticmethod
    def make_cache():
        all_data = Host.get_by()

        Rds.router().del_host_list()
        for host in all_data:
            Rds.router().set_host(host)

    @staticmethod
    def fetch_host(host_ip):
        # 当redis出错时直接返回mysql数据
        try:
            host_info = Rds.router(readonly=True).get_host(host_ip)
        except RedisExceptionError:
            host_info = Host.get_by(first=True, host_ip=host_ip)
        if host_info:
            return host_info

        host_info = Host.get_by(first=True, host_ip=host_ip)
        if host_info:
            Rds.router().set_host(host_info)
            return host_info
