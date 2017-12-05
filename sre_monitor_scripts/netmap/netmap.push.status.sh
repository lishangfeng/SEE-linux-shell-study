#!/bin/sh

echo 'ok'
o_metric='netmap.push.status'

o_sqlitef='/opt/cloud/workspace/netmap_host/push/sqlite'
o_services='
dns_server
vpc_controller
'

find_pids_dns_server() {
	pgrep -f '\<dns_server\>'
}

find_pids_vpc_controller() {
	cat /opt/cloud/workspace/run/vpc_controller.pid 2>/dev/null
}

find_identifiers_dns_server() {
	echo INTERNAL_DNS IP
}

find_identifiers_vpc_controller() {
	echo VPC_IP
}


__errmsg() {
	echo "$*" >&2
}

report_falcon() {
    local value=$1
    local metric="$o_metric"
    local endpoint=`hostname -a`
    local ts=$(date +%s)
    local step=60
    local tags=""
    local counterType="GAUGE"

    curl -s -X POST -d "[{\"metric\":\"$metric\", \"endpoint\":\"$endpoint\", \"timestamp\":$ts, \"step\":60, \"value\":$value, \"counterType\":\"$counterType\", \"tags\":\"$tags\"}]" "http://transfer.falcon.vip.sankuai.com:6060/api/push" | python -m json.tool
}

select_pids() {
	sqlite3 "$o_sqlitef" 'select pid from client_info_tbl;'
}

select_identifiers() {
	local pid="$1"

	sqlite3 "$o_sqlitef" "select identifier from identifier_watcher_tbl where watcher_clients like '%.$pid.%';"
}

check() {
	local service
	local pids pid
	local identifiers identifier
	local ok

	[ -f "$o_sqlitef" ] || return 0

	for service in $o_services; do
		eval "pids=\"\$(find_pids_$service)\""
		eval "identifiers=\"\$(find_identifiers_$service)\""

		ok=1
		for pid in $pids; do
			[ -n "$pid" -a -d "/proc/$pid" ] || continue

			ok=0
			select_pids | grep -q "\\<$pid\\>" || continue
			for identifier in $identifiers; do
				select_identifiers "$pid" | grep -q "\\<$identifier\\>" || {
					__errmsg "$service: no identifier $identifier"
					report_falcon 2
					return 2
				}
			done
			ok=2
			break
		done

		if [ "$ok" = 0 ]; then
			__errmsg "$service: pids: $pids are not found in client_info_tbl"
			report_falcon 1
			return 1
		elif [ "$ok" = 1 ]; then
			__errmsg "$service: not running"
			continue
		elif [ "$ok" = 2 ]; then
			continue
		else
			__errmsg "$service: bug, unexpected ok val: $ok"
		fi
	done

	report_falcon 0
	return 0
}

gendoc() {
	cat <<EOF
# $o_metric

## 概述

平台服务如vpc_controller, dns_server等，需要告知netmap_server服务，接收指定identifier的数据推送

netmap_server会在本地sqlite数据库中，记录监听者的pid、所监听的identifiers列表

以下情况任一出现时，判为异常

- netmap_server数据库中缺少服务的pid
- netmap_server数据库中缺少服务预期要监听的identifier

## 注意事项

- netmap_server数据库不存在时，不报警
- 服务自身未启动时（根据服务名无法找到其pid），不报警

## 处置方法

1. 确认netmap_server服务正常运行
2. 执行该脚本，若出现以下输出，则重启服务<service_name>

	   <service_name>: pids: <pids> are not found in ...
	   <service_name>: no identifier <identifier>

3. 继续执行该脚本，直至无错误输出
EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
