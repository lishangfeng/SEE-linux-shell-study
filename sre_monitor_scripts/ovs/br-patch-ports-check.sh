#!/bin/sh

source ./lib

o_metric="ovs.br.patch.ports.check"
step=60
tags=""

__errmsg() {
	echo "$*" >&2
}

check() {
	local brs br
	local basep subp
	local basebr subbr
	local missing

	# only proceed if br_t exists
	brs="$(ovs_list_br)"
	if ! echo "$brs" | grep -q '^br_t$'; then
		exit 0
	fi

	for br in $brs; do
		if [ "$br" != "br_t" ]; then
			basep="i-$br-p"
			basebr="$(ovs_find_br_with_port $basep)"
			[ "$basebr" == "br_t" ] && is_ovs_port_in_br $basep $basebr || missing="$missing $basep"

			subp="i-$br"
			subbr="$(ovs_find_br_with_port $subp)"
			[ "$subbr" == "$br" ] && is_ovs_port_in_br $subp $subbr || missing="$missing $subp"
		fi
	done

	if [ -z "$missing" ]; then
		report_falcon $o_metric 0 $step $tags
		exit 0
	else
		__errmsg "missing: $missing"
		report_falcon $o_metric 1 $step $tags
		exit 1
	fi
}

gendoc() {
	cat <<EOF
# $o_metric

## 概述

该脚本检查基础网桥br_t与各个子网桥间的patch port连接是否存在

EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
