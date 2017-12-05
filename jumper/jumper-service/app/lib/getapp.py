#!/bin/env python
# coding:utf-8

import json
import logging
import re
import urllib
import urllib2

from app.ssh_server.init import config


def gen_idc():
    idc_api = 'http://api.syscmdb.sankuai.com/api/v0.1/ci/s?q=_type:idc,&fl=idc_name,idc_alias&count=100'
    idcs = dict()
    result = json.loads(http_rpc(idc_api))
    for i in result['result']:
        idcs[i['idc_alias'].lower()] = i['idc_name']
    print json.dumps(idcs, indent=4).decode("unicode-escape")


def http_rpc(url, method='get', **kwargs):
    if method == 'post':
        headers = kwargs.get('headers', {})
        if kwargs.get('data'):
            headers.update({'Content-Type': 'content-type: text/plain'})
            data = json.dumps(kwargs.get('data'))
        else:
            data = urllib.urlencode(kwargs.get('values', {}))
        request = urllib2.Request(url, headers=headers, data=data)
    else:
        request = urllib2.Request(url, headers=kwargs.get('headers', {}))
    try:
        return urllib2.urlopen(request, timeout=int(kwargs.get('timeout', 10))).read().strip()
    except Exception, e:
        logging.warning(u'获取应用信息失败: {0}'.format(str(e)))


def get_app(service_name):
    hosts = list()
    cmdb = 'shanghai'
    shanghai_cmdb = 'http://api-cmdb.sankuai.com/api/v0.1/projects/{0}/devices?&count=500'
    beijing_cmdb = 'https://ops.sankuai.com/api/stree/tag/host?fields=mc_disk_size,cpus_number,idc,cluster,memory_size,ip_lan&{0}'

    # 解析应用
    # 北京 owt.pdl.srv.cluster
    # 上海 jumper-web
    nums = service_name.split('.')
    if len(nums) == 1:
        result = http_rpc(shanghai_cmdb.format(service_name), timeout=3)
        if result:
            members = json.loads(result)['devices']
            if not members:
                return u'找不到应用:{0}, 拼写错误? getapp查看帮助'.format(service_name), None
        else:
            return u'请求api-cmdb.sankuai.com接口失败', None

        for i in members:
            host = dict()
            if i.get('ci_type') == 'docker':
                host['name'] = i.get('private_ip')[0]
            else:
                host['name'] = i.get('hostname')

            host['ip'] = i.get('private_ip')[0]
            host['cpu'] = i.get('cpu_count', 'null')
            host['memory'] = i.get('ram_size', 'null')
            # host['type'] = i.get('vserver_type', 'docker')
            # host['status'] = i.get('status', 'null')
            host['idc'] = i.get('idc', 'null')
            host['env'] = i.get('env', 'null')
            hosts.append(host)
    elif len(nums) > 2:
        cmdb = 'beijing'
        if len(nums) == 3:
            reg = '^\w+.\w+.\w+$'
            if not re.match(reg, service_name):
                return u'请按搜索规则拼写查询名,如有疑问getapp查看帮助', None
            query = 'owt={0}&pdl={1}&srv={2}'.format(nums[0], nums[1], nums[2])
        elif len(nums) == 4:
            reg = '^\w+.\w+.\w+.\w+$'
            if not re.match(reg, service_name):
                return u'请按搜索规则拼写查询名,如有疑问getapp查看帮助', None
            query = 'owt={0}&pdl={1}&srv={2}&cluster={3}'.format(nums[0], nums[1], nums[2], nums[3])
        else:
            return u'请按搜索规则拼写查询名,如有疑问getapp查看帮助', None
        headers = dict(Authorization='Bearer d1b3ef487d9b8ca5a817443d77f217302c038b81')

        result = http_rpc(beijing_cmdb.format(query), timeout=5, headers=headers)
        if result:
            members = json.loads(result)['data']
            if not members:
                return u'节点:{0}找不到机器，请检查后查询'.format(service_name), None
            for i in members:
                host = dict()
                host['ip'] = i.get('ip_lan')
                host['name'] = i.get('name')
                host['idc'] = config['idc'].get(i['idc'], 'null')
                host['cpu'] = i.get('cpus_number', 'null')
                host['memory'] = i['memory_size'].replace(' ', '')
                host['cluster'] = i.get('cluster', 'null')
                host['disk'] = i.get('mc_disk_size', 'null')
                hosts.append(host)
        else:
            return u'请求ops.sankuai.com接口失败', None
    else:
        return u'请按搜索规则拼写查询名,如有疑问getapp查看帮助', None
    return hosts, cmdb


def get_host(host):
    if re.match('\s*\d+\.\d+\.\d+\.\d+\s*', host):
        return get_ip(host)
    elif host.endswith('.sankuai.com'):
        host = host.split('.')[0]
        return gethost(host)
    else:
        return gethost(host)


def gethost(host):
    headers = dict(Authorization='Bearer d1b3ef487d9b8ca5a817443d77f217302c038b81')
    cmdb_detail = 'http://ops.sankuai.com/api/host/detail/{0}'
    cmdb_admin = 'https://ops.sankuai.com/api/stree/host/admin?host={0}'

    #查询主机信息
    _tmp = http_rpc(cmdb_detail.format(host), timeout=3, headers=headers)
    if not _tmp:
        return u'请求api-ops.sankuai.com接口失败'
    result = json.loads(_tmp).get('data')
    if not result:
        return u'CMDB找不到对应主机信息({0})，请检查后查询'.format(host)

    # 查询负责人信息
    tmp_ = http_rpc(cmdb_admin.format(host), timeout=3, headers=headers)
    if not tmp_:
        return u'请求api-ops.sankuai.com接口失败'
    admin = json.loads(tmp_)['data'][host]

    info = dict()
    info['name'] = result.get('name')
    info['ip'] = result.get('ip_lan')
    info['host_type'] = u'物理机' if result.get('host_type') == True  else u'虚拟机'
    info['cpu'] = result.get('cpus_number', 'null')
    info['memory'] = result['memory_size'].replace(' ', '')
    info['disk'] = result.get('disk_size') + 'GB' if result.get('disk_size') != u'' else u'未找到'
    info['sn'] = result.get('sn')
    info['os'] = result.get('os')
    info['kernel'] = result.get('kernel')
    info['purchase_at'] = result.get('purchase_at')
    info['idc'] = result.get('idc')
    info['rd'] = admin.get('rd_admin') if admin.get('rd_admin') != u'' else u'未找到'
    info['ep'] = admin.get('ep_admin') if admin.get('ep_admin') != u'' else u'未找到'
    info['op'] = admin.get('op_admin') if admin.get('op_admin') != u'' else u'未找到'

    return info


def get_ip(host_ip):
    headers = dict(Authorization='Bearer d1b3ef487d9b8ca5a817443d77f217302c038b81')
    cmdb_ip = 'https://ops.sankuai.com/api/host/list?ip_lan={0}'

    #查询ip得到host
    tmp = http_rpc(cmdb_ip.format(host_ip), timeout=3, headers=headers)
    if not tmp:
        return u'请求api-ops.sankuai.com接口失败'
    member = json.loads(tmp)['data']
    if not member:
        return u'CMDB找不到对应IP信息({0})，请检查后查询'.format(host_ip)

    host = member[0].get('name')
    return gethost(host)

if __name__ == "__main__":
    # print json.dumps(get_app('tuangou-web'), indent=4)
    #print json.dumps(get_app('banma.admin.finance'), indent=4)
    # gen_idc()
    get_ip('10.12.48.12')
