%define debug_package %{nil}
Name:       jumper-pam
Version:    vv
Release:    rr
Summary:    nss library and pam_python module for jumper
License:    GNU Software License
Group:      System Environment/Libraries
Source0:    pam.tar.gz
Requires:   jansson, pam
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root

%description
nss & pam module

%prep
%setup -n %name-%version

%build
source /etc/profile
cd nss-http     && make      && cd ..
cd pam-python   && make lib  && cd ..

[ -d build ] || mkdir build
cp pam-python/src/pam_python.so         build
cp nss-http/.libs/libnss_http.so.2.0    build

%install
rm -rf          %{buildroot}
mkdir -p        %{buildroot}/sbin
mkdir -p        %{buildroot}/usr/sbin/
mkdir -p        %{buildroot}/lib64/security
mkdir -p        %{buildroot}/etc/pam.d
mkdir -p        %{buildroot}/etc/init.d
mkdir -p        %{buildroot}/var/lib/nss-cache

cp                conf/nsswitch.conf        %{buildroot}/etc/nsswitch.conf.temp
cp                conf/system-auth-ac       %{buildroot}/etc/pam.d/system-auth-ac.temp
cp                conf/password-auth-ac     %{buildroot}/etc/pam.d/password-auth-ac.temp
install -D -m 644 conf/nss-http.conf        %{buildroot}/etc/nss-http.conf
install -D -m 755 conf/nss-cache.sh         %{buildroot}/etc/init.d/nss-cache
install -D -m 755 build/libnss_http.so.2.0  %{buildroot}/lib64/libnss_http.so.2.0
install -D -m 755 build/pam_python.so       %{buildroot}/lib64/security/pam_python.so
install -D -m 755 pam-python/auth.py        %{buildroot}/lib64/security/auth.py
install -D -m 700 sudo/getsudo.py           %{buildroot}/sbin/getsudo
install -D -m 700 tools/repair-jumper.sh     %{buildroot}/sbin/repair-jumper
install -D -m 700 get-nss/get-nss           %{buildroot}/usr/sbin/get-nss
install -D -m 700 get-sudo/get-sudo         %{buildroot}/usr/sbin/get-sudo
install -D -m 750 nss-cache/nss-cache       %{buildroot}/usr/sbin/nss-cache


%clean
rm -rf ${buildroot}


# 安装后执行
%post
#!/bin/bash
set -e
if ! grep -q "http" /etc/nsswitch.conf >>/dev/null 2>&1;then
    cp /etc/nsswitch.conf.temp /etc/nsswitch.conf
fi

if ! grep -q "pam_python.so" /etc/pam.d/system-auth-ac >>/dev/null 2>&1;then
    cp /etc/pam.d/system-auth-ac.temp /etc/pam.d/system-auth-ac
fi

if ! grep -q "pam_python.so" /etc/pam.d/password-auth-ac >>/dev/null 2>&1;then
    cp /etc/pam.d/password-auth-ac.temp /etc/pam.d/password-auth-ac
fi

cd /etc/pam.d/
[ -L system-auth ] || ln -sf system-auth-ac system-auth
[ -L password-auth ] || ln -sf password-auth-ac password-auth

mkdir -p /var/lib/nss-cache

ln -sf /lib64/libnss_http.so.2.0     /lib64/libnss_http.so.2
ln -sf /lib64/libnss_http.so.2.0     /lib64/libnss_http.so
ldconfig


# install
if [ "$1" = "1" ]; then
    chkconfig --add nss-cache
    chkconfig nss-cache on
    service nss-cache restart
# upgrade
elif [ "$1" = "2" ]; then
    printf "\033[0;36mnss-cache upgrade done\n\033[0m"
    service nss-cache restart
fi


# 清理过去的nss-cache日志
[ -d /var/log/ ] && rm -f /var/log/nss-cache.log.201*
echo > /dev/null
# 清理过旧的进程信息
[ -d /var/lib/nss-cache/data ] && rm -rf /var/lib/nss-cache/data
echo > /dev/null
# 清理python nss-cache.py main过旧的进程
old_pid=`ps aux|grep "python nss-cache.py main" |grep -v 'grep'|awk '{print $2}'`
if [ "$old_pid" != "" ];then
    kill $old_pid
fi
echo > /dev/null


# 触发sudo更新一次
/usr/sbin/get-sudo
printf "\033[0;36mcache sudoers file done \n\033[0m"
echo > /dev/null

# restart crontab 重新加载lib库
service crond restart

# 卸载前执行
%preun
if [ "$1" = "0" ];then
    service nss-cache stop
fi
echo > /dev/null


# 卸载后执行
%postun
#!/bin/bash
set -e
if [ "$1" = "0" ];then
    [ -L /lib64/libnss_http.so ] && rm /lib64/libnss_http.so
    [ -L /lib64/libnss_http.so.2 ] && rm /lib64/libnss_http.so.2
    [ -d /var/lib/nss-cache ] && rm -rf /var/lib/nss-cache
fi
echo > /dev/null

%files
%defattr(-,root,root,-)
/sbin/getsudo
/sbin/repair-jumper
/var/lib/nss-cache/
/usr/sbin/nss-cache
/usr/sbin/get-nss
/usr/sbin/get-sudo
/lib64/security/
/lib64/libnss_http.so.2.0
/etc/nss-http.conf
/etc/init.d/nss-cache
/etc/nsswitch.conf.temp
/etc/pam.d/password-auth-ac.temp
/etc/pam.d/system-auth-ac.temp


%changelog
* Fri Oct 20 2017 alex.wan <alex.wan@dianping.com> 2.8.5-1
- [Bugfix] 修复get-nss命令请求远程接口出错时将空文件写入本地缓存文件
- [Bugfix] 修复go-logger日志模块在多进程情况下切割文件失败问题
- [Feature] 清理过去的nss-cache日志，清理过去的/var/lib/nss-cache目录文件
- [Feature] 清理过去的python nss-cache.py main进程
- [Feature] 只允许sshd进程访问远程接口获取账号信息

* Tue Aug 15 2017 alex.wan <alex.wan@dianping.com> 2.8-1
- go优化内存版，大约30M以内
- 新增/usr/sbin/get-nss, /usr/sbin/get-sudo命令供nss-cache daemon进程外部调用
- nss-http内部移除无用字段
- 新增检查和修复脚本 repair-jumper
- 开启http监听接口，支持修改内存配置，查看内存账号信息

* Mon Jun 12 2017 alex.wan <alex.wan@dianping.com> 2.7-1
- 使用go重写nss-cache部分,同时优化启动脚本

* Wed May 10 2017 alex.wan <alex.wan@dianping.com> 2.4-1
- fix crond fork child process bug

* Tue Apr 27 2017 alex.wan <alex.wan@dianping.com> 2.3-1
- fix nss-http.c封装json格式数据溢出
- fix nss-cache线程异常退出
- fix pid文件存在进程不存在的情况下启动进程失败
- upgrade 安装rpm包时触发一次getsudo
- upgrade 创建软连接

* Tue Feb 28 2017 alex.wan <alex.wan@dianping.com> 2.2-1
- fix host_ip函数获取机器ip顺序调整, 改为首先从dns获取;
- fix configPaser 获取配置存在的bug
- 优化nss-cache进程启动名更改成 python nss-cache.py daemon
- 优化nss-cache拉取缓存的随机时间, randint(time - 600, time)
- 优化nss-cache进程挂的情况下能够获取完整的用户信息和组信息
- 优化nss-cache进程start和stop时写pid文件

* Thu Jan 12 2017 alex.wan <alex.wan@dianping.com> 2.0-1
- 写死缓存目录, 写死socket类型, 规范目录

* Wed Dec 21 2016 alex.wan <alex.wan@dianping.com> 1.8-1
- 规范rpm打包

* Tue Dec 20 2016 alex.wan <alex.wan@dianping.com> 1.7-1
- 修复subprocess获取sudo时导致centos7无法登陆成功
- 拆分auth和account接口

* Sun Nov 27 2016 alex.wan <alex.wan@dianping.com> 1.5-1
- 修复auth.py鉴权取ip地址不准确
- 修复sudo接口产生僵死进程
- 修复sudo文件权限为0660无法使用的情况
- 修复rpm更新执行脚本失败导致的更新失败
- 优化nss-cache缓存对异常情况的兼容以及日志提示
- 优化libcurl超时设置
- 去除rpm包conflict

* Wed Sep 21 2016 alex.wan <alex.wan@dianping.com> 1.0-1
- first edition v1.0-1
