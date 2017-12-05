#!/bin/env python
# -*- coding:utf-8 -*-

rules = dict()

# view.auth
rules['auth_add'] = {
    'post': dict(
            required=['role', 'role_id', 'label', 'label_key'],
            optional=['auth_type', 'life_cycle', 'protocol'],
            one_of={'role': ['user', 'group'], 'label': ['host_ip', 'host_fqdn', 'host_name', 'cluster', 'srv', 'pdl', 'owt']}
    )
}
rules['auth_update'] = {
    'get': dict(
            required=['id']
    ),
    'post': dict(
            optional=['auth_type', 'life_cycle', 'protocol'] + ['role', 'role_id', 'label', 'label_key']
    )
}
rules['web_auth'] = {
    'get': dict(
            required=['uid']
    )
}

# view.cmdb
rules['ssh_cmdb'] = {
    'post': dict(
            required=['project']
    )
}

# view.group
rules['group_add'] = {
    'post': dict(
            required=['group_name', 'desc'],
            optional=['gid', 'user_list', 'type'],
            param_type={'user_list': list}
    )
}
rules['group_delete'] = {
    'post': dict(
            required=['group_name'],
            optional=['user_list'],
            param_type={'user_list': list}
    )
}
rules['group_update'] = {
    'post': dict(
            required=['group_name', 'user_list'],
            param_type={'user_list': list}
    )
}

# view.host
rules['host_corp'] = {
    'post': dict(
            required=['host']
    )
}
rules['host_add'] = {
    'post': dict(
            required=['host_name', 'host_ip', 'host_fqdn'],
            optional=['corp', 'owt', 'pdl', 'srv', 'cluster', 'host_port', 'host_type']
    )
}
rules['host_flush'] = {
    'get': dict(
            required=['host_ip'],
            optional=['flush']
    )
}
rules['host_update'] = {
    'get': dict(
            required=['id']
    ),
    'post': dict(
            optional=['corp', 'owt', 'pdl', 'srv', 'cluster', 'host_ip'] +
                     ['host_name', 'host_fqdn', 'host_port', 'host_type'],
            empty=['pdl', 'srv', 'cluster']
    ),
}

# view.nss
rules['nss'] = {
    'get': dict(
            optional=['uid', 'user_name', 'gid', 'group_name'] + ['user_id', 'host_ip', 'host_name']
    )
}
rules['nss_cache_flush'] = {
    'post': dict(
            optional=['user_list', 'group_list'],
            param_type={'user_list': list, 'group_list': list}
    )
}

# view.pam
rules['pam_password'] = {
    'get': dict(
            required=['user_name'],
            optional=['host_ip', 'host_name']
    ),
    'post': dict(
            required=['password']
    )
}
rules['pam_account'] = {
    'get': dict(
            required=['user_name', 'host_ip', 'host_name', 'login']
    )
}

# view.sudo
rules['sudo_add'] = {
    'post': dict(
            required=['role', 'role_name', 'label', 'label_key'],
            optional=['hosts', 'users', 'password_option', 'commands', 'life_cycle'],
            one_of={'role': ['user', 'group'], 'label': ['host_ip', 'host_fqdn', 'host_name', 'cluster', 'srv', 'pdl', 'owt']}
    )
}

# 上海sudo个性化接口
rules['sh_sudo_add'] = {
    'post': dict(
            required=['user_name', 'sudo_type', 'data'],
            one_of={'sudo_type': ['host', 'project']}
    )
}
rules['sankuai_sudo_add'] = {
    'post': dict(
            required=['user_name', 'sudo_type', 'data'],
            one_of={'sudo_type': ['host', 'project']}
    )
}
rules['sudo_update'] = {
    'get': dict(
            required=['id']
    ),
    'post': dict(
            optional=['role', 'role_name', 'label', 'label_key', 'hosts'] +
                     ['users', 'password_option', 'commands', 'life_cycle']
    )
}

rules['sudo_info'] = {
    'get': dict(
            required=['user_id', 'host_ip', 'host_name']
    )
}

rules['sudo_config'] = {
    'get': dict(
            required=['host_ip', 'host_name']
    )
}

rules['sudo_cache'] = {
    'get': dict(
            required=['host_ip', 'host_name']
    )
}

# views.user
rules['user_top'] = {
    'get': dict(
            optional=['limit', 'interval', 'duration'],
            param_type={'limit': int, 'interval': int, 'duration': int}

    )
}
rules['user_add'] = {
    'post': dict(
            required=['user_name'],
            optional=['gid', 'uid', 'role'],
            one_of={'role': ['sa', 'op', 'sre', 'srd', 'qa', 'rd']}
    )
}
rules['user_update'] = {
    'post': dict(
            optional=['email', 'mobile', 'type', 'role', 'desc', 'enable', 'source', 'public_key', 'login_time'],
            one_of={'role': ['sa', 'op', 'sre', 'srd', 'qa', 'rd']}
    )
}
rules['bulk_del_user'] = {
    'post': dict(
            required=['user_list'],
            param_type={'user_list': list}
    )
}
rules['web_user_update'] = {
    'post': dict(
            optional=['email', 'mobile', 'organization']
    )
}
rules['user_update_uid'] = {
    'post': dict(
            required=['uid']
    )
}

rules['user_reset_password'] = {
    'post': dict(
            required=['user_name']
    )
}
rules['sync_user'] = {
    'post': dict(
            required=['user_name']
    )
}
rules['unlocking_user'] = {
    'post': dict(
            required=['user_name']
    )
}
rules['user_session'] = {
    'get': dict(
            required=['smoke'],
            optional=['user_name']
    )
}

# view.jumper
rules['jumper_update_password'] = {
    'post': dict(
            required=['query_string', 'data']
    )
}

# 待定接口, 后期可以删除
rules['user_jumper_update'] = {
    'post': dict(
            required=['query_string', 'data']
    )
}

rules['login_history_add'] = {
    'post': dict(
            required=['jumper_name', 'host_name', 'host_port', 'remote_ip'] +
                     ['remote_port', 'user_name', 'login_name', 'user_uid', 'login_uuid', 'login_time'],
            optional=['host_type', 'login_type', 'channel_id', 'session_uuid']
    )
}

rules['login_history_update'] = {
    'post': dict(
            required=['query_string', 'data']
    )
}

rules['login_history_get'] = {
    'get': dict(required=['user_uid'])
}

rules['get_host_history'] = {
    'get': dict(
            required=['user_uid'],
            optional=['page']
    )
}

rules['get_user_history'] = {
    'POST': dict(
            required=['host_list', 'start_time', 'end_time'],
            param_type={'host_list': list}
    )
}

rules['jumper_uuid_set'] = {
    'post': dict(
            required=['connection_info', 'source']
    )
}

rules['jumper_uuid_get'] = {
    'get': dict(
            required=['uuid', 'source']
    )
}

rules['jumper_uuid_del'] = {
    'post': dict(
            required=['uuid', 'source']
    )
}

rules['jumper_history_add'] = {
    'post': dict(
            required=['login_name', 'commands_list']
    )
}

rules['jumper_history_get'] = {
    'get': dict(
            required=['login_name']
    )
}

rules['permission_del'] = {
    'post': dict(
            required=['key']
    )
}

rules['permission_get'] = {
    'get': dict(
            required=['key']
    )
}

rules['onetime_password'] = {
    'post': dict(
            required=['password']
    )
}

rules['onetime_token'] = {
    'post': dict(
            required=['origin', 'user_name'],
            optional=['host_name']
    )
}

rules['lock_user'] = {
    'post': dict(
            required=['login_name', 'lock_user_ttl']
    )
}

rules['unlock_user'] = {
    'post': dict(
            required=['login_name']
    )
}

rules['get_command'] = {
    'get': dict(
            required=['host', 'start_time', 'end_time'],
            optional=['username']
    )
}

rules['command_history_delete'] = {
    'get': dict(
            optional=['user_name', 'login_name', 'exec_time', 'host_name',
                      'command', 'danger', 'login_uuid', 'session_uuid']
    )
}

rules['save_script'] = {
    'post': dict(
            required=['script']
    )
}