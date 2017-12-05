#!/bin/env python
# -*- coding:utf-8 -*-

import json
import time
import requests

from flask import current_app as app


class Falcon:
    api_domain = u'http://query.falcon.vip.sankuai.com:9966'
    # api_domain = u'http://10.5.233.113:9966'
    api = dict(
        chart_data={
            'desc': u'用于查询falcon打点数据',
            'url': '/graph/history'
        }
    )

    def __init__(self, **kwargs):
        pass

    @classmethod
    def get_chart_data(cls, duration=15):
        end = int(time.time())
        start = end - 24 * 3600 * duration
        query_dict = dict(
            end=end,
            start=start,
            cf="MAX",
            endpoint_counters=[{'endpoint': app.config['ENDPOINT'], 'counter': counter}
                                                for counter in app.config['COUNTER_LIST']])
        try:
            result = requests.get(cls.api_domain + cls.api['chart_data']['url'], data=json.dumps(query_dict)).json()
            if isinstance(result, dict) and result.get('msg'):
                app.logger.warning(u'Falcon 历史数据接口返回数据错误: {0}'.format(result['msg']))
                return ''
            else:
                values = dict()
                if result:
                    for chart_data in result:
                        try:
                            for value in chart_data['Values']:
                                temp = time.strftime("%m-%d %H:%M", time.localtime(value['timestamp']))
                                value['timestamp'] = temp
                        except:
                            chart_data['Values'] = []
                        values[chart_data['counter']] = chart_data['Values']
                return values
        except Exception, e:
            app.logger.warning(u'调用 Falcon 接口失败: {0}'.format(str(e)))
