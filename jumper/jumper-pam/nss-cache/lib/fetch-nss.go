package lib

import (
    "fmt"
    "strconv"
    "encoding/json"
    "jumper-pam/nss-cache/conf"
    "github.com/thevipwan/go-logger/logger"
)

type User struct {
    Pw_Uid  int
    Pw_dir  string
    Group   map[int]UserGroup
    Pw_name string
}

type UserGroup struct {
    Gr_name string
    Gr_gid  int
}

type Group struct {
    Gr_name string
    Gr_gid  int
    Gr_mem  []string
}

type Result struct {
    Version string
    Group   []Group
    User    []User
    Delete  []string
}

/* 版本格式 */
type NssData struct {
    Code   int
    Msg    string
    Result Result
}

/* 单个用户格式 */
type NssUserData struct {
    Code   int
    Result User
}

/* 单个组格式 */
type NssGroupData struct {
    Code   int
    Result Group
}

func FetchNss(version string) (nss_data NssData, err error) {
    ua := "NSS-CACHE"
    hostname, ip := HostInfo()
    cache_server := conf.Config.Get("cache_server")
    timeout, _ := strconv.Atoi(conf.Config.Get("cache_timeout", "30").(string))
    url := fmt.Sprintf("%s/api/nss/cache?version=%s&host_ip=%s&host_name=%s", cache_server, version, ip, hostname)
    data, err := Http("GET", url, ua, timeout)
    if err != nil {
        logger.Error("获取nss缓存数据失败", err.Error())
        return
    }

    err = json.Unmarshal(data, &nss_data)
    if err != nil {
        logger.Error("格式化NSS数据失败", err.Error(), url)
    }
    return
}

func FetchNssUser(key string, _type string) (nss_user NssUserData, err error) {
    ua := "NSS-CACHE"
    hostname, ip := HostInfo()
    cache_server := conf.Config.Get("cache_server")
    timeout, _ := strconv.Atoi(conf.Config.Get("cache_timeout", "30").(string))
    var url string
    if _type == "id" {
        url = fmt.Sprintf("%s/api/nss?uid=%s&host_ip=%s&host_name=%s", cache_server, key, ip, hostname)
    } else {
        url = fmt.Sprintf("%s/api/nss?user_name=%s&host_ip=%s&host_name=%s", cache_server, key, ip, hostname)
    }

    data, err := Http("GET", url, ua, timeout)
    if err != nil {
        logger.Error("获取nss缓存数据失败", err.Error(), url)
        return
    }

    err = json.Unmarshal(data, &nss_user)
    if err != nil {
        logger.Error("格式化NSS数据失败", err.Error(), url)
    }
    return
}

func FetchNssGroup(key string, _type string) (nss_group NssGroupData, err error) {
    ua := "NSS-CACHE"
    hostname, ip := HostInfo()
    cache_server := conf.Config.Get("cache_server")
    timeout, _ := strconv.Atoi(conf.Config.Get("cache_timeout", "30").(string))
    var url string
    if _type == "id" {
        url = fmt.Sprintf("%s/api/nss?gid=%s&host_ip=%s&host_name=%s", cache_server, key, ip, hostname)
    } else {
        url = fmt.Sprintf("%s/api/nss?group_name=%s&host_ip=%s&host_name=%s", cache_server, key, ip, hostname)
    }

    data, err := Http("GET", url, ua, timeout)
    if err != nil {
        logger.Error("获取nss缓存数据失败", err.Error(), url)
        return
    }

    err = json.Unmarshal(data, &nss_group)
    if err != nil {
        logger.Error("格式化NSS数据失败", err.Error(), url)
    }
    return
}
