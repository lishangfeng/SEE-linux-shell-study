# -*- coding: utf-8 -*-

import socket
import requests
import time
import json


ENDPOINT = 'jumper-service01.gq'
DATA_URL = "https://jumper.dper.com/api/monitor?smoke=true"
PUSH_URL = "http://127.0.0.1:1988/v1/push"


ret = requests.get(DATA_URL).json()
data = ret['result']
ts = int(time.time())
payload = [
    {
        "endpoint": ENDPOINT,
        "metric": "backend_online",
        "timestamp": ts,
        "step": 60,
        "value": data['backend_online'],
        "counterType": "GAUGE",
        "tags": "",
    },

    {
        "endpoint": ENDPOINT,
        "metric": "dp_session_online",
        "timestamp": ts,
        "step": 60,
        "value": data['dp_session_online'],
        "counterType": "GAUGE",
        "tags": "",
    },
    {
        "endpoint": ENDPOINT,
        "metric": "mt_session_online",
        "timestamp": ts,
        "step": 60,
        "value": data['mt_session_online'],
        "counterType": "GAUGE",
        "tags": "",
    },

    {
        "endpoint": ENDPOINT,
        "metric": "dp_user_online",
        "timestamp": ts,
        "step": 60,
        "value": data['dp_user_online'],
        "counterType": "GAUGE",
        "tags": "",
    },
    {
        "endpoint": ENDPOINT,
        "metric": "mt_user_online",
        "timestamp": ts,
        "step": 60,
        "value": data['mt_user_online'],
        "counterType": "GAUGE",
        "tags": "",
    },
]
r = requests.post(PUSH_URL, data=json.dumps(payload))
