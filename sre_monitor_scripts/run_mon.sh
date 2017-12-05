#!/bin/bash

source ./lib

o_script_dir="/opt/meituan/external_scripts"
o_lock_dir="/tmp"


run_script() {
    local project="$1"
    local script="$2"
    local script_name=`echo $script | awk -F'/' '{printf $NF}'`
    local script_path=`echo $script | sed "s/$script_name//"`

    pushd $script_path > /dev/null
    if [ -n "$o_debug" ] && [ "$o_debug" -gt 0 ]; then
        echo "flock -x -e -w 10 ${o_lock_dir}/${project}.${script_name}.lock -c $script"
    else
        chmod +x "$script"
        flock -x -e -w 10 "${o_lock_dir}/${project}.${script_name}.lock" -c "$script"
    fi
    popd > /dev/null
}


find_script() {
    find_path="$1"
    find "$find_path" -maxdepth 1 -type f 2>/dev/null
}

run_cron_for_project() {
    local project="$1"
    local project_dir="${o_script_dir}/${project}"

    pushd $project_dir > /dev/null

    date_minute=`date '+%M'`
    if [ $((10#$date_minute % 30)) -eq 29 ]; then
        for script in `find_script "${project_dir}/30_min"`; do
            run_script $project $script
        done
    fi
    if [ $((10#$date_minute % 5)) -eq 2 ]; then
        for script in `find_script "${project_dir}/5_min"`; do
            run_script $project $script
        done
    fi
    for script in `find_script "${project_dir}"`; do
        run_script $project $script
    done

    popd > /dev/null
}


# role is compute node
if [ `process_exist "host_server"` -eq 1 ]; then
    run_cron_for_project "netmap"
    run_cron_for_project "ovs"
    run_cron_for_project "controller"
fi

# role is vrouter node
if [ `process_exist "vrouter_server"` -eq 1 ]; then
    run_cron_for_project "vrouter"
fi

# role is network-controller
if [ `process_exist "crawfish"` -eq 1 ]; then
    run_cron_for_project "crawfish"
fi

# role is defense
if [ `hostname | grep defense-controller | wc -l` -eq 1 ]; then
    run_cron_for_project "defense"
fi

# role is network-controller
if [ `process_exist "/home/mgw/bin/load_balancer"` -eq 1 ]; then
    run_cron_for_project "mgw"
fi

# role is secutiry
if [ `process_exist "security_services"` -eq 1 ]; then
    run_cron_for_project "security"
elif [ `process_exist "flow_detector.py"` -eq 1 ]; then
    run_cron_for_project "security"
elif [ `process_exist "blackdragservices.py"` -eq 1 ]; then
    run_cron_for_project "security"
fi
