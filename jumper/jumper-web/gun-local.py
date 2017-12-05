# -*- coding: utf-8 -*-

import os
import multiprocessing

app_name = 'jumper-web'

# listen address
bind = "0.0.0.0:8080"

basedir = os.path.abspath(os.path.dirname(__file__))

# pid file
pidfile = '{0}/gunicorn.pid'.format(basedir)

# worker number
workers = 4

# gevent, sync, eventlet, tornado
worker_class = 'gevent'

# The maximum number of pending connections.
backlog = 2048

# run backend
daemon = True

timeout = 60

# loglevel debug|info|warning|error|critical
loglevel = 'info'

# access log location
accesslog = '/tmp/gunicorn-access.log'

# error log location
errorlog = '/tmp/gunicorn-error.log'

# access log format
# x-real-ip头 远程ip 请求时间 请求方法和string 状态码 返回字节 请求时间(毫秒) UA referer
access_log_format = "%({x-real-ip}i)s %(h)s %(t)s %(r)s %(s)s %(B)s %(L)s %(a)s %(f)s"

# gunicorn 日志格式
"""
Identifier	Description
	h		remote address
	l		'-'
	u		user name
	t		date of the request
	r		status line (e.g. GET / HTTP/1.1)
	m		request method
	U		URL path without query string
	q		query string
	H		protocol
	s		status
	B		response length
	b		response length or '-' (CLF format)
	f		referer
	a		user agent
	T		request time in seconds
	D		request time in microseconds
	L		request time in decimal seconds
	p		process ID
{Header}i	request header
{Header}o	response header
"""
