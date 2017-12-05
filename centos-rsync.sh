#!/bin/bash

LOCATION=/opt/meituan/repos/centos
LOCK=/opt/meituan/repos/00scripts/lock/centos-rsync.lock
EXCLUDE=/opt/meituan/repos/00scripts/centos.exclude


echo "-----------------------------------"
echo `date +"%F %T"` "CentOS rsync Start."

# Use a lock file to assure that a job is not already running.
if [ -f $LOCK ]; then
    echo `date +"%F %T"` "CentOS rsync already running."
    exit 0
fi

# Rsync the CentOS repo.
touch $LOCK

#rsync -rlgoDzH --partial --delete --stats --exclude-from $EXCLUDE --chmod=Du=rwx,Dgo+rx,Fu=rw,Fgo+r rsync://rsync.mirrors.ustc.edu.cn/centos $LOCATION
#rsync -rlgoDzH --partial --delete --stats --exclude-from $EXCLUDE --chmod=Du=rwx,Dgo+rx,Fu=rw,Fgo+r rsync://mirrors.hust.edu.cn/centos $LOCATION

rsync -azH --no-owner --partial --delete \
      --delete-after --delay-updates \
      --verbose --stats \
      --bwlimit 85600 \
      --exclude-from $EXCLUDE \
      rsync://rsync.mirrors.ustc.edu.cn/centos $LOCATION
      #rsync://mirrors.yun-idc.com/centos $LOCATION

rm -f $LOCK

echo `date +"%F %T"` "CentOS rsync End."
