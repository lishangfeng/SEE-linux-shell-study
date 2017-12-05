package lib

import (
    "path"
    "io/ioutil"
    "github.com/thevipwan/go-logger/logger"
    "jumper-pam/nss-cache/conf"
)

func NssLoad() (nss_data []byte, version []byte) {
    var err error
    cache_dir := conf.Config.Get("cache_dir", "/var/lib/nss-cache").(string)
    nss_data, err = ioutil.ReadFile(path.Join(cache_dir, "cache.db"))
    if err != nil {
        version = []byte("xx-xx-xx-xx")
        logger.Warn("读取本地缓存失败, ", err.Error())
    } else {
        version, _ = ioutil.ReadFile(path.Join(cache_dir, "version"))
        logger.Warn("读取本地缓存 ", string(version))
    }
    return
}
