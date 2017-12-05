package main

import (
    "runtime"
    "jumper-pam/nss-cache/nss"
    "jumper-pam/nss-cache/cache"
    "jumper-pam/nss-cache/lib"
    "jumper-pam/nss-cache/conf"
    "jumper-pam/nss-cache/http"
    "jumper-pam/nss-cache/outside"
    "github.com/thevipwan/go-logger/logger"
)


func init() {
    lib.InitLogger()
    runtime.GOMAXPROCS(runtime.NumCPU())
}

func main() {
    logger.Info("启动程序")
    lib.WritePid(conf.Config.Get("pid_file", "/var/run/nss-cache.pid").(string))
    go cache.NssCache()
    go outside.NSS()
    go outside.Sudo()
    go http.HttpServer()
    nss.SocketServer()
}
