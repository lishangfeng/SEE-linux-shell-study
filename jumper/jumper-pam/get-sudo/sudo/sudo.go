package sudo

import (
    "io/ioutil"
    "os"
    "jumper-pam/nss-cache/conf"
    "jumper-pam/get-sudo/lib"
    "github.com/thevipwan/go-logger/logger"
    "path"
)

func SudoCache() {
    //sudo_file := path.Join("/tmp/", conf.Config.Get("sudoer_file").(string))
    sudo_file := path.Join("/etc/sudoers.d/", conf.Config.Get("sudoer_file").(string))
    result, err := lib.FetchSudo()
    if err != nil {
        logger.Error("[get-sudo] 更新sudo配置失败: ", err)
    } else if result == "empty" {
        logger.Warn("[get-sudo] 该机器不存在sudo配置")
        os.Remove(sudo_file)
    } else {
        os.Create(sudo_file)
        ioutil.WriteFile(sudo_file, []byte(result), 0440)
        logger.Info("[get-sudo] 更新sudo配置成功")
    }
}
