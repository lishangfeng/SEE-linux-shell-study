package http

import (
    "time"
    "runtime"
    "jumper-pam/nss-cache/model"
    "jumper-pam/nss-cache/outside"
    "jumper-pam/nss-cache/cache"
    "os"
)

var startTime time.Time

func init()  {
    startTime = time.Now()
}

func GatherInfo() interface {}{
    /*   进程线程数       pending
         进程内存占用     pending
         进程启动时间
         操作系统版本     pending
         用户和组统计数
         PID
         jumper-pam版本
         最近nss缓存更新时间
         最近nss缓存版本号
         最近sudo缓存更新时间
    */

    info := make(map[string]interface{})
    var user_count int
    var group_count int
    for _, i := range model.NssIndexName{
        if i.Type == "user"{
            user_count += 1
        }else if i.Type == "group" {
            if len(i.Members)>0{
                group_count += 1
            }
        }
    }

    info["pid"] = os.Getpid()
    tfmt := "2006-01-02 15:04:05"
    info["start_time"] = startTime.Format(tfmt)
    info["user_count"] = user_count
    info["group_count"] = group_count
    if cache.LastNssTime.IsZero() {
        info["latest_nss"] = "尚未执行"
    }else{
        info["latest_nss"] = cache.LastNssTime.Format(tfmt)
    }
    if outside.LastSudoTime.IsZero() {
        info["latest_sudo"] = "尚未执行"
    }else{
        info["latest_sudo"] = outside.LastSudoTime.Format(tfmt)
    }
    info["os_version"] = runtime.GOOS
    info["hostname"], _ = os.Hostname()
    info["nss_version"] = cache.Version
    info["rpm_version"] = "pam-version"      // 打包时替换
    //info["memory_used"] = "200M"
    //info["threads_count"] = 20
    return info
}
