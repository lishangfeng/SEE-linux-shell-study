#!/usr/bin/python

import os
import re
import time
import json
import logging
import requests
import datetime
from socket import gethostname


def report_to_falcon(metric, value, tags):
    time_stamp = int(time.time())
    hostname = gethostname().split('.')[0]
    payload = [{
              "endpoint"  : hostname,
              "metric"    : metric,
              "timestamp" : time_stamp,
              "step"      : 60,
              "value"     : value,
              "counterType": "GAUGE",
              "tags"      : tags,
              }]
    response = requests.post('http://transfer.falcon.vip.sankuai.com:6060/api/push', json=payload)
    return response


def run_command(command):
    return os.popen(command).read().split('\n')[:-1]


def format_resource_info(old_resource_info):
    resource_info = {'cpu_usage': {},
                     'newconns': -1,
                     'currentconns': -1,
                     'ports': {}}

    for line in old_resource_info:
        if line.strip().startswith('current_conns'):
            resource_info['currentconns'] = line.split()[-1]
        elif line.strip().startswith('new_conns'):
            resource_info['newconns'] = line.split()[-1]
        elif line.strip().startswith('cpu'):
            cpu_id = line.split()[1]
            cpu_usage = line.split()[-1]
            resource_info['cpu_usage'][cpu_id] = cpu_usage
        elif line.strip().startswith('total'):
            ports = []
            for port in line.split():
                resource_info['ports'][port] = {}
                ports.append(port)
        elif re.match('^(inpps)|(outpps)|(inbps)|(outbps)', line):
            key = line.split()[0]
            data = line.split()[1:]
            for port_index in range(len(data)):
                resource_info['ports'][ports[port_index]][key] = data[port_index]

    return resource_info


def get_resource_info():
    get_resource_info_command = '/sbin/mgwadm --list --resource'
    resource_info = run_command(get_resource_info_command)
    return format_resource_info(resource_info)


def main():
    resource_info = get_resource_info()

    report_to_falcon('mgw.currentconns', resource_info['currentconns'], 'service=mgw')
    report_to_falcon('mgw.newconns', resource_info['newconns'], 'service=mgw')

    for cpu_id in resource_info['cpu_usage'].keys():
        tags = 'cpuid=%s' %cpu_id
        report_to_falcon('mgw.cpu.usage.percent', resource_info['cpu_usage'][cpu_id], tags)

    for port in resource_info['ports']:
        for key in resource_info['ports'][port].keys():
            metric = 'mgw.%s' %key
            tags = 'interface=%s' %port
            report_to_falcon(metric, resource_info['ports'][port][key], tags)


if __name__ == '__main__':
    main()
