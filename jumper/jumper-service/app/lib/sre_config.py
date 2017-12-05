# -*- coding: utf-8 -*-

from app.ssh_server.init import config

template = u"""******* 服务器基础配置 *******\r
监听端口：{ssh_server_port}\r
监听地址：{ssh_server_ip}\r
lion环境：{app_env}\r
工作模式：{server_type}\r
pid文件: {pid_file}\r
日志级别：{log_level} \r
日志大小：{log_size}\r
日志路径：{log_file}\r
日志份数：{log_rotate_backup_count}\r
开启二次验证：{dynamic_password} \r
发送大象消息: {dx_code}\r

******* 用户基础设置 *******\r
大象新闻：{terminal_news}\r
密码过期：{password_ttl}天\r
会话心跳：{ssh_keep_alive}s\r
最长断线时间：{vacant_timeout}s\r
密码输错次数：6次\r
密码错误恢复：{lock_user_ttl}s\r
历史命令条数：{history_size}\r
pssh连接超时：{pssh_timout}s\r
ssh 命令端口：{ssh_backend_port}\r
管理员角色：{admin_role}\r
报警管理员：{admin_user}\r
危险命令管理员：{warning_user}\r

******* 第三方系统接口 *******\r
Jumper\r
主API: {api_domain}\r
takecare_api: {takecare}\r

hr系统接口：{ops_auth}\r

谷歌认证系统\r
google_auth_api: {google_auth_api}\r
network_interface: {network_interface}\r

录屏设置\r
录像保存份数：{recorder_number}份\r
录像上传地址：{mss_server}\r
"""


def dir_config():
    return template.format(**config)
