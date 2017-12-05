#!/bin/sh

source ./lib

o_metric="ovs.dpctl.flood.check"
step=60
tags=""

export PATH=/usr/local/bin:$PATH

# bad one
#
#	recirc_id(0),skb_priority(0),in_port(6),eth(src=00:22:0f:4a:e7:66,dst=00:22:be:29:b3:5b),eth_type(0x0800),ipv4(src=10.32.182.245/255.0.0.0,dst=10.32.182.164/255.0.0.0,proto=6/0xff,tos=0/0,ttl=64/0,frag=no/0xff), packets:7, bytes:467, used:0.126s, flags:P., actions:sample(sample=0.1%,actions(userspace(pid=4294955305,sFlow(vid=0,pcp=0,output=2147483658)))),1,2,4,5,7,9,10,11,8,3
#
# match:
#
# - dl_dst unicast
# - packets non-zero
# - actions output to more than 1 port
#
RE_eth='\<eth(src=[0-9a-f:]\+,dst=[0-9a-f][02468ace][0-9a-f:]\+)'
RE_packets='\<packets:[1-9][0-9]*'
RE_actions='\<actions:[^ ]*\([0-9]\+\(,[0-9]\+\)\+\)'
RE_=".*,$RE_eth.*, $RE_packets, .*$RE_actions"
check() {
	if ovs_dp_dumpflows_all | grep -q --max-count=1 "$RE_"; then
		report_falcon $o_metric 1 $step $tags
	else
		report_falcon $o_metric 0 $step $tags
	fi
}

gendoc() {
	cat <<EOF
# $o_metric

## 概述

该脚本检查datapath flows列表，找到可能导致异常泛洪的规则，然后报警

规则如下

 - 二层单播：$RE_eth
 - 流表被匹配至少1次：$RE_packets
 - 报文输出端口数超过1个：$RE_actions

例如

	recirc_id(0),skb_priority(0),in_port(6),eth(src=00:22:0f:4a:e7:66,dst=00:22:be:29:b3:5b),eth_type(0x0800),ipv4(src=10.32.182.245/255.0.0.0,dst=10.32.182.164/255.0.0.0,proto=6/0xff,tos=0/0,ttl=64/0,frag=no/0xff), packets:7, bytes:467, used:0.126s, flags:P., actions:sample(sample=0.1%,actions(userspace(pid=4294955305,sFlow(vid=0,pcp=0,output=2147483658)))),1,2,4,5,7,9,10,11,8,3
EOF
}

[ "$#" -gt 0 ] || set -- check
"$@"
