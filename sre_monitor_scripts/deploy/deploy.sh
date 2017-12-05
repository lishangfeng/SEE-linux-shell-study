#!/bin/bash

set -x

pre_check() {
    sed -i '/external_scripts.*run_cron.sh/d' /var/spool/cron/root
}

main() {
    grep 'bash run_mon.sh' /var/spool/cron/root

    if [ $? -eq 0 ]; then
        echo 'cron has been exist.'
    else
        echo '*/1 * * * * cd /opt/meituan/external_scripts && bash run_mon.sh &> /dev/null' >> /var/spool/cron/root
    fi

    echo 'deploy success'
}

pre_check
main

