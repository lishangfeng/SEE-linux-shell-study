#!/usr/bin/python
# encoding=utf-8

import hmac
import time
import base64
import hashlib

from app.lib.http_client import http_client


class Notice:
    def __init__(self, body, receivers):
        self.client_id = '0513021Rv2124712'
        self.client_secret = '415be4e6561846323d5fc48b83fa7a2c'
        self.sender = 'xinmeida_noc@meituan.com'
        # 内网
        self.dx_api = 'http://xm-in.sankuai.com/api/message'
        # 外网
        # self.dx_api = 'http://dxapi.sankuai.com/xai/message'

        self.receivers = receivers.split(',')
        self.body = body
        self.dx()

    def mail(self):
        pass

    def sms(self):
        pass

    def dx(self):
        data = {
            'sender': self.sender,
            'receivers': self.receivers,
            'body': self.body,
            'type': 'text/plain'
        }
        http_client(url=self.dx_api, json=data, headers=self.get_dx_header(), method='put')

    def get_dx_header(self):
        date_format = '%a, %d %b %Y %H:%M:%S'
        date = time.strftime(date_format, time.gmtime()) + " GMT"
        string_to_sign = "PUT /api/message\n" + date
        signature = base64.encodestring(hmac.new(self.client_secret, string_to_sign, hashlib.sha1).digest())
        authorization = "MWS" + " " + self.client_id + ":" + signature.replace("\n", "")
        url_headers = {'Content-type': 'application/json;charset=utf-8', 'Date': date, 'Authorization': authorization}
        return url_headers


if __name__ == '__main__':
    Notice(u'test', receivers='kui.xu@dianping.com')
