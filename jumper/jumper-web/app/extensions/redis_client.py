# -*- coding: utf-8 -*-

from app.lib.app_redis import AppRedis, redis_map


class NewRedis(object):
    def __init__(self):
        pass

    def init_app(self, app):
        max_connections = app.config.get('MAX_CONNECTIONS', 50)
        for key, value in app.config['REDIS_POOL'].items():
            if isinstance(value, list):
                redis_map['readonly'] = list()
                for x in value:
                    r = AppRedis.from_url(x, max_connections=max_connections, socket_connect_timeout=1)
                    redis_map['readonly'].append(r)
            else:
                r = AppRedis.from_url(value, max_connections=max_connections, socket_connect_timeout=1)
                redis_map.update({key: r})
        else:
            redis_map['readonly'].append(redis_map['default'])

extension = NewRedis()
