package lib

import (
    "github.com/thevipwan/go-logger/logger"
    "jumper-pam/nss-cache/conf"
    "path"
)

func InitLogger() {
    lg := map[string]logger.LEVEL{
        "INFO":  logger.INFO,
        "DEBUG": logger.DEBUG,
        "WARN":  logger.WARN,
        "ERROR": logger.ERROR,
        "FATAL": logger.FATAL,
    }
    logger.SetConsole(false)
    log_file := conf.Config.Get("log_file", "/var/log/nss-cache.log").(string)
    logger.SetRollingFile(path.Dir(log_file), path.Base(log_file), 3, 10, logger.MB)
    logger.SetLevel(lg[conf.Config.Get("log_level", "DEBUG").(string)])
}
