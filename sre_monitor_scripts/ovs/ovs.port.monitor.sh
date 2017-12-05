#! /bin/bash

o_metric="ovs.port.monitor"

source ./lib

check() {
	local dpports="$(ovs_dp_ports)"
	local dbports="$(ovs_vsctl --columns=name find Interface 'type!=patch' | grep -oE '[^ ]+$' | tr -d '"')"
	local bad=0
	local br ifname
	local ovs_dpdk_running="$(is_ovs_dpdk_running && echo 1)"

	for br in $(ovs_list_br); do
		for ifname in $(ovs_list_ports "$br"); do
			if ! echo "$dpports" | grep -q "\<$ifname\>\s[0-9]\\+/[0-9a-z]\\+:"; then
				__errmsg "$br $ifname: exist in ovs-vsctl output but not in the datapath"
				__errmsg "	sudo /usr/local/bin/ovs-vsctl del-port $br $ifname"
				if [ -d "/sys/class/net/$ifname" ]; then
					__errmsg "	sudo /usr/local/bin/ovs-vsctl add-port $br $ifname"
				fi
				bad=1
			fi
		done
	done
    report_falcon_common $o_metric "$bad"
}

gendoc() {
    cat <<EOF
# $o_metric

## 概述

对于ovs-vsctl list-br, list-ports获取的所有port，判断是否在ovs-appctl dpif/show中存在，不存在则报警

## 处置

异常时，程序会输出错误信息，以及建议的恢复命令

	o_debug=1 ./${o_metric}.sh
	o_debug=1 ./${o_metric}.sh 2>&1 | grep '^\t'
	o_debug=1 ./${o_metric}.sh 2>&1 | grep '^\t' | bash -s

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
