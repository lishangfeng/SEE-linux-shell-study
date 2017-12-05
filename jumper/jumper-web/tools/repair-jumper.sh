#!/usr/bin/env bash
# 终端颜色
Red='\033[0;31m'
Color_Off='\033[0m'
Green='\033[0;32m'

#printf "${Green}开始检查jumper-pam是否正常工作${Color_Off}\n"
#printf "${Green}------------------------------------${Color_Off}\n"

check_rpm_install(){
    if rpm -qi jumper-pam >/dev/null 2>&1;then
        version=`rpm -qa|grep jumper-pam`
        printf "${Green}[rpm安装包] $version ${Color_Off}\n"
    elif rpm -qi dp-pam > /dev/null 2>&1;then
        version=`rpm -qa|grep dp-pam`
        printf "${Red}[rpm安装包] 版本过旧$version ${Color_Off}\n"
    else
        printf "${Red}[rpm安装包] 未安装,下面修复安装${Color_Off}\n"
        yum install -y jumper-pam >/dev/null 2>&1
        if [ $? -eq 0 ];then
            printf "${Green}[rpm安装包] 最新版rpm安装成功${Color_Off}\n"
        else
            printf "${Red}[rpm安装包] rpm安装失败, 程序退出，请手动执行yum install -y jumper-pam排查${Color_Off}\n"
            exit 1
        fi
    fi
}

check_nss_cache(){
    if pidof /usr/sbin/nss-cache>/dev/null 2>&1;then
        printf "${Green}[nss-cache] 正常${Color_Off}\n"
    else
        printf "${Red}[nss-cache] 服务未启动，尝试拉起服务${Color_Off}\n"
        service nss-cache restart>/dev/null 2>&1
        if ! pidof /usr/sbin/nss-cache>/dev/null 2>&1;then
            printf "${Red} 服务启动失败,请手动执行service nss-cache restart排查${Color_Off}\n"
            exit 1
        fi
        printf "${Green}[nss-cache] 服务拉起成功${Color_Off}\n"
    fi
}

check_sock_file(){
    pid_file=`cat /var/run/nss-cache.pid`
    if [ -S /var/run/nss-cache.sock ];then
        if lsof -p $pid_file |grep /var/run/nss-cache.sock > /dev/null 2>&1;then
            printf "${Green}[sock-file] 正常${Color_Off}\n"
        else
            printf "${Red}[sock-file] /var/run/nss-cache.sock文件未和进程nss-cache绑定,尝试重启服务修复${Color_Off}\n"
            service nss-cache restart >/dev/null 2>&1
            if [ -S /var/run/nss-cache.sock ];then
                printf "${Red}[sock-file] /var/run/nss-cache.sock文件不存在,重启修复失败，请手动排查${Color_Off}\n"
                exit 1
            fi
            printf "${Green}[sock-file] 修复成功${Color_Off}\n"
        fi
    else
        printf "${Red}[sock-file] /var/run/nss-cache.sock文件不存在,尝试重启服务修复${Color_Off}\n"
        service nss-cache restart >/dev/null 2>&1
        if [ -S /var/run/nss-cache.sock ];then
            printf "${Red}[sock-file] /var/run/nss-cache.sock文件不存在,重启修复失败，请手动排查${Color_Off}\n"
            exit 1
        fi
        printf "${Green}[sock-file] 修复成功${Color_Off}\n"
    fi
}

check_selinux(){
    status=`getenforce`
    if [ "$status" != "Disabled" ];then
        printf "${Red}[ Selinux ] 状态为非关闭，尝试修复${Color_Off}\n"
        setenforce 0 >/dev/null 2>&1
        status=`getenforce`
        if [ "$status" != "Disabled" ];then
            printf "${Red}[ Selinux ] 状态为非关闭，请手动排查{Color_Off}\n"
            exit 1
        fi
        printf "${Green}[ Selinux ] 关闭SELinux成功${Color_Off}\n"
    else
        printf "${Green}[ Selinux ] 正常${Color_Off}\n"
    fi
}

check_nsswitch(){
    if grep -q "http" /etc/nsswitch.conf >>/dev/null 2>&1;then
        printf "${Green}[nsswitch ] 正常${Color_Off}\n"
    else
        cp /etc/nsswitch.conf.temp /etc/nsswitch.conf
        if ! grep -q "http" /etc/nsswitch.conf >>/dev/null 2>&1;then
            printf "${Red}[nsswitch ] /etc/nsswitch.conf配置不正常，请手动排查${Color_Off}\n"
            exit 1
        fi
        printf "${Green}[nsswitch ] 修复成功${Color_Off}\n"
    fi
}

check_libnss_http_so(){
    if [ -f /lib64/libnss_http.so.2.0 ] && [ -L /lib64/libnss_http.so.2 ] && [ -L /lib64/libnss_http.so ];then
        printf "${Green}[动态链接库] 正常${Color_Off}\n"
    else
        printf "${Red}[动态链接库] 不正常，尝试修复${Color_Off}\n"
        ln -sf /lib64/libnss_http.so.2.0     /lib64/libnss_http.so.2
        ln -sf /lib64/libnss_http.so.2.0     /lib64/libnss_http.so
        ldconfig
        if ! [ -f /lib64/libnss_http.so.2.0 ] && [ -L /lib64/libnss_http.so.2 ] && [ -L /lib64/libnss_http.so ];then
            printf "${Red}[动态链接库] 修复失败，请手动排查${Color_Off}\n"
            exit 1
        fi
        printf "${Green}[动态链接库] 修复成功${Color_Off}\n"
    fi
}

check_pam_config(){
    if [ -f /etc/pam.d/system-auth-ac ] && [ -L /etc/pam.d/system-auth ] && [ -f /etc/pam.d/password-auth-ac ] && [ -L /etc/pam.d/password-auth ];then
        printf "${Green}[ pam 配置 ] 正常${Color_Off}\n"
    else
        [ -L system-auth ] || ln -sf system-auth-ac system-auth
        [ -L password-auth ] || ln -sf password-auth-ac password-auth

        if ! [ -f /etc/pam.d/system-auth-ac ] && [ -L /etc/pam.d/system-auth ] && [ -f /etc/pam.d/password-auth-ac ] && [ -L /etc/pam.d/password-auth ];then
            printf "${Red}[pam 配置 ] 修复失败，请手动排查${Color_Off}\n"
            exit 1
        fi
    fi
}

check_nscd_password(){
    if grep enable-cache /etc/nscd.conf|grep passwd|grep no >/dev/null 2>&1;then
        printf "${Green}[nscd配置 ] 正常${Color_Off}\n"
    else
        printf "${Red}[nscd配置 ] 错误配置,开启passwd缓存和jumper冲突，尝试手动修复${Color_Off}\n"
        exit 1
    fi
}


main(){
check_rpm_install
check_nss_cache
check_sock_file
check_nsswitch
check_selinux
check_nscd_password
check_libnss_http_so
check_pam_config
echo
printf "${Green}\t+------------------------------------------------------+${Color_Off}\n"
printf "${Green}\t+                                                      +${Color_Off}\n"
printf "${Green}\t+ 所有关键配置及服务检测正常, 如还有疑问请联系:        +${Color_Off}\n"
printf "${Green}\t+      alex.wan,tanxiaohang,pengjunyu                  +${Color_Off}\n"
printf "${Green}\t+                                                      +${Color_Off}\n"
printf "${Green}\t+------------------------------------------------------+${Color_Off}\n"
echo
}

main
