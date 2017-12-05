package main

import (
    "path"
    "jumper-pam/testing/test_logger"
    "time"
)

func main()  {
    test_logger.SetConsole(false)
    log_file := "/tmp/nss-cache.log"
    test_logger.SetRollingFile(path.Dir(log_file), path.Base(log_file), 3, 1, test_logger.KB)
    test_logger.SetLevel(test_logger.DEBUG)
    for {
        test_logger.Debug("hahah")
        time.Sleep(time.Duration(1) * time.Second)
    }
}