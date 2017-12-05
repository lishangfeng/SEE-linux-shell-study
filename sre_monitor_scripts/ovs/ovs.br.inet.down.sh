#!/bin/sh

source ./lib

o_metric='ovs.br.inet.down'

__errmsg() {
	echo "$*" >&2
}

should_check_br() {
	local br="$1"

	case "$br" in
		brpri|breip|brpub)
			return 0
			;;
		*)
			return 1
			;;
	esac
}

check() {
	local RE_flags='.*<\([^>]\+\)>.*$'
	local RE_inet='.*inet \([0-9.]\+\)\/[0-9]\+ .*'
	local br
	local ipa flags inet
	local up has_inet has_local_route
	local bad any_bad=0

	for br in $(ovs_vsctl list-br); do
		if ! should_check_br "$br"; then
			continue
		fi

		ipa="$(ip address show "$br")"
		bad=0

		flags="$(echo "$ipa" | sed -n -e "0,/${RE_flags}/s//\\1/p")"
		if echo "$flags" | tr , '\n' | grep -q -m1 '\<UP\>'; then
			up=1
		else
			up=0
			bad=1
		fi

		inet="$(echo "$ipa" | sed -n -e "0,/${RE_inet}/s//\\1/p")"
		if [ -n "$inet" ]; then
			has_inet=1
			if ip route get "$inet" | grep -m1 -q "^local "; then
				has_local_route=1
			else
				has_local_route=0
				bad=1
			fi
		else
			has_inet=0
			has_local_route=0
			bad=1
		fi

		[ "$bad" != "0" ] || any_bad=1
		report_falcon_common "$o_metric" "$bad" "br=$br"
		[ "$bad" = 0 ] || {
			__errmsg "bad: br=$br,up=$up,has_inet=$has_inet,has_local_route=$has_local_route"
		}
	done

	return "$any_bad"
}

gendoc() {
	cat <<EOF
# $o_metric

## 概述

该脚本检查宿主机上brpri, breip, brpub网桥，若网桥存在，且和以下任一条件冲突，则报警

 - ip address输出的网桥flags中，必须包含UP
 - ip address输出的网桥地址中，必须包含一项inet地址
 - ip route get \$inet的路由指向必须是本地

该检查主要用来避免host-dns因网桥配置不当造成无法为guest服务的情况

## 处置方法

重启host_server
EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
