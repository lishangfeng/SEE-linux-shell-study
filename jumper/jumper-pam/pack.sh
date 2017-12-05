#!/usr/bin/env bash

echo "交互式打包工具为您服务:"

while true
do
    read -p "输入打包版本, 例如: 1.0.0, 2.1.0, 3.3.1: " version
    case $version in
        [1-9].[0-9].[0-9]) break ;;
        *) echo "版本输入错误,请重新输入";;
    esac
done

echo "打包版本为:${version}"
echo "即将为你编译rpm包, 并且存放至/root/目录下"

echo "系统环境准备"
yum install jansson jansson-devel python-devel pam-devel rpm-build -y

# 创建golang编译环境
mkdir -p /root/golang/src /root/golang/pkg /root/golang/bin
export PATH=/usr/local/go/bin:$PATH
export GOPATH=/root/golang
cd /root/golang/src && rm jumper-pam -rf && git clone ssh://git@git.dianpingoa.com/dpop-app/jumper-pam.git
#cd jumper-pam && git checkout -b test origin/test && cd ..
#cd /root/golang/src && rm jumper-pam -rf && cp -a ~/jumper-pam .
# 清理git
rm -rf jumper-pam/.git

#创建目录
mkdir -p SOURCES SPECS

rpm_version="jumper-pam-"${version}

# user_agent for nss-cache 里面包含公司和版本信息
cache_ua=`echo "GO-NSS-CACHE-"${version} | tr [:lower:] [:upper:]`
# user_agent for nss-auth
auth_ua=`echo "GO-NSS-AUTH-"${version} | tr [:lower:] [:upper:]`
# user_agent for nss-sudo
sudo_ua=`echo "GO-GET-SUDO-"${version} | tr [:lower:] [:upper:]`


# 根据提供的版本替换ua
sed -i "s/NSS-CACHE/${cache_ua}/g" jumper-pam/nss-cache/lib/utlis.go
sed -i "s/pam-version/${rpm_version}/g" jumper-pam/nss-cache/http/utlis.go
sed -i "s/NSS-CACHE/${cache_ua}/g" jumper-pam/nss-cache/lib/fetch-nss.go
sed -i "s/SUDO-CACHE/${sudo_ua}/g" jumper-pam/get-sudo/lib/fetch-sudo.go
sed -i "/User-Agent/s/NSS-AUTH/${auth_ua}/g" jumper-pam/pam-python/auth.py

cd jumper-pam/get-nss && go get && go build && cd ../..
cd jumper-pam/get-sudo && go get && go build && cd ../..
cd jumper-pam/nss-cache && go get && go build && cd ../..

# system version
system_version=el`uname -r|head -n1|awk -F[el] '{print $3}'|awk -F[.] '{print $1}'`

# 根据系统类型替换spec文件
sed -i "1, /Version:/s/vv/${version}/" jumper-pam/rpmbuild/jumper-pam.spec
sed -i "1, /Source0:/s/pam.tar.gz/${rpm_version}.tar.gz/" jumper-pam/rpmbuild/jumper-pam.spec
sed -i "1, /Release:/s/rr/1.${system_version}/" jumper-pam/rpmbuild/jumper-pam.spec

# 根据打包的公司替换spec配置文件
cp jumper-pam/rpmbuild/jumper-pam.spec ./SPECS/

# 准备source文件
rm -rf $rpm_version
mv jumper-pam $rpm_version
tar zcvf $rpm_version.tar.gz $rpm_version
mv $rpm_version.tar.gz SOURCES

# 开始打包
rpmbuild --define '_topdir %(echo $PWD)' -ba ./SPECS/jumper-pam.spec

# 将打包文件拷贝至/root下
cp RPMS/x86_64/${rpm_version}-1.${system_version}.x86_64.rpm ~
