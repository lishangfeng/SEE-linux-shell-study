#!/bin/env python
# -*- coding:utf-8 -*-

from flask import current_app as app


def history_filter(login_info):
    try:
        login_info.pop('id')
        login_info.pop('jumper_name')
        login_info.pop('host_type')
        login_info.pop('host_port')
        login_info.pop('remote_ip')
        login_info.pop('remote_port')
        login_info.pop('user_uid')
        login_info.pop('login_type')
        login_info.pop('login_uuid')
        login_info.pop('channel_id')
    except KeyError:
        pass
    return login_info

