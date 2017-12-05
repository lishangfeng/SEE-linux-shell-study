#!/bin/bash
 
IFS=$'\n'
BRIDGE=brpri
 
function get_field_value {
    LINE=$1
    FILED=$2
    VALUE_RAW=$(echo $LINE | grep -o "\<$FILED=\([^,]\+\)")
    echo ${VALUE_RAW#*=}
}
 
ALL_PORTS=$(sudo /usr/local/bin/ovs-ofctl show $BRIDGE)
PHY_PORT=$(echo $ALL_PORTS | grep -o -m 1 "\<[0-9]\+(\(bond0\.[0-9]\+\|i-$BRIDGE\)):" | cut -d'(' -f 1)
 
ALLOW_FLOWS=$(sudo /usr/local/bin/ovs-ofctl dump-flows $BRIDGE 'dl_dst=01:00:00:00:00:00/01:00:00:00:00:00' | grep -i 'output\|controller')
PPS_VALUE_MAX=0
for FLOW in $ALLOW_FLOWS; do
    IN_PORT=$(get_field_value "$FLOW" in_port)
    if [ -n $IN_PORT ]; then
        if [ -n $PHY_PORT ]; then
            if [[ $IN_PORT = $PHY_PORT ]]; then
                continue
            fi
        else
            echo $ALL_PORTS | grep -i -q "\<$IN_PORT(\(n\|e\)-[0-9a-z]\+):"
            if [ $? -ne 0 ]; then
                continue
            fi
        fi
    fi
    DURATION=$(echo $(get_field_value "$FLOW" duration) | sed 's/[^.0-9]*//g')
    N_PACKETS=$(get_field_value "$FLOW" n_packets)
    PPS_VALUE=$(echo "$N_PACKETS / $DURATION" | bc -l)
    if [ $(echo "$PPS_VALUE > $PPS_VALUE_MAX " | bc) -eq 1 ]; then
        PPS_VALUE_MAX=$PPS_VALUE
    fi
done
PPS_VALUE_MAX1=`printf '%.0f\n' $PPS_VALUE_MAX`
e=`hostname -a`
m="dump_flows_pps_value_max"
t=""
ts=`date +%s`
curl -s -X POST -d "[{\"metric\":\"$m\", \"endpoint\":\"$e\", \"timestamp\":$ts,\"step\":120, \"value\":$PPS_VALUE_MAX1, \"counterType\":\"GAUGE\",\"tags\":\"$t\"
}]" "transfer.falcon.vip.sankuai.com:6060/api/push" | python -m json.tool
