#!/bin/sh
export PAHT=$PATH:/usr/sbin

o_metric="vlan_filter_status"

report_falcon() {
	value=$1
	NIC=$2
	metric="$o_metric"
	endpoint=`hostname -a`
	ts=$(date +%s)
	step=60
	counterType="GAUGE"

    curl -s -X POST -d "[{\"metric\":\"$metric\", \"endpoint\":\"$endpoint\", \"timestamp\":$ts, \"step\":60, \"value\":$value, \"counterType\":\"$counterType\", \"tags\":\"nic=$NIC\"}]" "http://transfer.falcon.vip.sankuai.com:6060/api/push"|python -m json.tool

}

__errmsg() {
	echo "$*" >&2
}

check() {
	local fmasters='/sys/class/net/bonding_masters'
	local fslaves
	local foperstate
	local bond slave
	local ethd
	local ucast_promisc mcast_promisc vlan_filter
	local bad_slaves
	local ok

	while read bond; do
		fslaves="/sys/class/net/$bond/bonding/slaves"
		for slave in $(cat $fslaves); do
			# only check those in up state
			foperstate="/sys/class/net/$slave/operstate"
			[ "$(cat "$foperstate")" = "up" ] || continue

			ok=1
			ethd="$(sudo ethtool -d "$slave")"
			ucast_promisc="$(echo "$ethd" | grep -i -m1 "Unicast Promiscuous" | awk '{ print $3 }')"
			mcast_promisc="$(echo "$ethd" | grep -i -m1 "Multicast Promiscuous" | awk '{ print $3 }')"

			if [ "$ucast_promisc" = "enabled" -o "$mcast_promisc" = "enabled" ]; then
				vlan_filter="$(echo "$ethd" | grep -i -m1 "VLAN Filter" | awk '{ print $3 }')"
				if [ "$vlan_filter" = "enabled" ]; then
					ok=0
					__errmsg "$slave: Unicast Promiscuous: $ucast_promisc, Multicast Promiscuous: $mcast_promisc, VLAN Filter: $vlan_filter"
					bad_slaves="$bad_slaves $slave"
					# this is the recommended way to restore
					sudo ifconfig "$slave" up
				fi
			fi
			report_falcon "$ok" "$slave"
		done
	done <"$fmasters"

	[ -z "$bad_slaves" ]
}

gendoc() {
	cat <<EOF
# $o_metric

## 概述

通过ethtool检查bonding中的网卡寄存器状态，当出现符合以下全部条件的网卡时，报警并尝试恢复

 - 网卡"Unicast Promiscuous"或"Multicast Promiscuous"状态为enabled
 - 网卡"VLAN Filter"状态为enabled

## 处置方法

发现异常时，脚本会通过ifconfig xxx up的方式尝试恢复
EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
