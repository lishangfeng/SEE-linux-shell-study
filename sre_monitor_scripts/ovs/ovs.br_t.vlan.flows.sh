#!/bin/bash

o_metric='ovs.br_t.vlan.flows'

source ./lib

ovs_get_port_tag_init_cache() {
	cmd_cache_local "__cache_ovs_get_port_tag" \
			ovs_vsctl --columns=name,tag find Port "tag!=[]"
}

ovs_get_port_tag() {
	local port_name="$1"; shift
	local awkexp='
			$1 == "name" {
				gsub(/"/, "", $3)
				port_name=$3
			}

			$1 == "tag" {
				if (arg_name == port_name) {
					print $3
					exit
				}
			}
		'

	echo "$__cache_ovs_get_port_tag" \
		| awk -v arg_name="$port_name" "$awkexp"
}

ovs_get_ofport_no_init_cache() {
	local br="$1"; shift
	local varname="__cache_ovs_get_ofport_no_$br"

	cmd_cache_local "$varname" \
			ovs_ofctl show "$br"
}

ovs_get_ofport_no() {
	local br="$1"; shift
	local port_name="$1"; shift
	local varname="__cache_ovs_get_ofport_no_$br"

	eval echo '"$'"$varname"'"' \
		| sed -n -e '0,/\s*\([0-9]\+\)'"($port_name):.*/s//\1/p"
}

check() {
	local port_name_phy
	local port_no_phy
	local port_tag_flows
	local brs br
	local port_name
	local port_no
	local port_tag
	local bad=0

	if is_ovs_dpdk_running; then
		port_name_phy=dpdkb2
	else
		port_name_phy=bond0
	fi

	ovs_get_ofport_no_init_cache br_t
	port_no_phy="$(ovs_get_ofport_no br_t "$port_name_phy")"
	if [ -z "$port_no_phy" ]; then
		__errmsg "cannot find port_no_phy in br_t: $port_name_phy"
		return 1
	fi

	# leftover flows will be ignored
	port_tag_flows="$(ovs_of_dumpflows_with_br br_t | sed -n -e 's/^\s*cookie=0x0, .* \(priority=1000,.*\)/\1/p')"
	brs="$(ovs_vsctl list-br | grep -v -E 'br_t|bradm')"

	ovs_get_port_tag_init_cache
	for br in $brs; do
		port_name="i-$br-p"
		port_no="$(ovs_get_ofport_no br_t "$port_name")"
		port_tag="$(ovs_get_port_tag "$port_name")"
		if [ "$port_tag" = 0 ]; then
			continue
		fi
		if [ -z "$port_tag" -o -z "$port_no" ]; then
			__errmsg "cannot find port tag or port no: name: $port_name, tag: $port_tag, port_no: $port_no"
			continue
		fi
		if ! check_fix_port_tag_flows "$port_tag_flows" "$port_tag" "$port_no" "$port_no_phy"; then
			bad=1
		fi
	done

	report_falcon_common "$o_metric" "$bad"
	return "$bad"
}

check_fix_port_tag_flows() {
	local port_tag_flows="$1"; shift
	local port_tag="$1"; shift
	local port_no="$1"; shift
	local port_no_phy="$1"; shift
	local r=0

	# - actions have order
	# - existence check, no uniqueness assurance
	if ! echo "$port_tag_flows" \
			| grep "in_port=$port_no\>" \
			| grep "mod_vlan_vid:$port_tag\>,output:$port_no_phy\>" \
			>/dev/null; then
		r=1
	fi

	if ! echo "$port_tag_flows" \
			| grep "in_port=$port_no_phy\>" \
			| grep "dl_vlan=$port_tag\>" \
			| grep "strip_vlan,output:$port_no\>" \
			>/dev/null; then
		r=1
	fi

	if [ "$r" = 1 ]; then
		ovs_ofctl add-flows br_t - <<-EOF
			priority=1000,in_port=$port_no_phy,dl_vlan=$port_tag actions=strip_vlan,output:$port_no
			priority=1000,in_port=$port_no actions=mod_vlan_vid:$port_tag,output:$port_no_phy
		EOF
	fi

	return "$r"
}

gendoc() {
	cat <<EOF
# $o_metric

## 概述

在宿主机网桥br_t中，对每个VLAN，都对应有2条流表，用于定向转发带VLAN的报文到指定端口

	# 从vpc网桥来的报文，打上VLAN tag走物理口出去
	priority=1000,in_port=17 actions=mod_vlan_vid:755,output:1

	# 从物理口来的带VLAN tag的报文，去掉tag，送到vpc网桥
	priority=1000,in_port=1,dl_vlan=755 actions=strip_vlan,output:17

对于宿主机上的带tag的网桥，包括brpri, breip, vpc网桥, 公共服务网桥brvpcsrv等，检查在br_t上是否存在以上2条流表。若有缺失，则报警

## 处置方法

脚本会自动添加缺失的流表

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
