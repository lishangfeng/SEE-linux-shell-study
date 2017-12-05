package outside

import (
    "time"
    "os/exec"
    "jumper-pam/nss-cache/conf"
    "jumper-pam/nss-cache/lib"
    "github.com/thevipwan/go-logger/logger"
)


func Run(cmd string){
	 exec.Command(cmd).Output()
}

var LastSudoTime time.Time


func NSS() {
    // first step in sleep 10min
    lib.RandSleep("600")
    for {
        logger.Info("[nss-cache] 调用外部命令 /usr/sbin/get-nss")
        Run("/usr/sbin/get-nss")
        lib.RandSleep(conf.Config.Get("interval_local", "86400").(string))
    }
}

func Sudo() {
    // first step in sleep 10min
    lib.RandSleep("600")
    for {
        logger.Info("[nss-cache] 调用外部命令 /usr/sbin/get-sudo")
        Run("/usr/sbin/get-sudo")
        LastSudoTime = time.Now()
        lib.RandSleep(conf.Config.Get("sudo_random", "1200").(string))
    }
}
