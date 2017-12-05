package lib

import (
    "errors"
    "strconv"
    "fmt"
    simple "github.com/bitly/go-simplejson"
    "jumper-pam/nss-cache/conf"
    "jumper-pam/nss-cache/lib"
)

func FetchSudo() (string, error) {
    // err != nil
    // sudo = 'empty' --> remove sudo file

    hostname, ip := lib.HostInfo()
    ua := "SUDO-CACHE"
    api := fmt.Sprintf("%s/api/sudo/cache?host_name=%s&host_ip=%s", conf.Config.Get("sudo_server"), hostname, ip)
    timeout, _ := strconv.Atoi(conf.Config.Get("sudo_timeout").(string))

    data, err := lib.Http("GET", api, ua, timeout)
    if err != nil {
        return "", errors.New("http response err")
    }

    // 非json数据格式，返回错误
    json_data, err := simple.NewJson(data)
    if err != nil {
        return "", errors.New("http response not json data")
    }

    // 校验code 200
    if code, _ := json_data.Get("code").Int(); code != 200 {
        msg, errs := json_data.MarshalJSON()
        if errs == nil {
            return "", errors.New("code != 200, 返回数据:" + string(msg))
        } else {
            return "", errors.New("code != 200")
        }
    }

    // 返回result如果是 [] 则表明机器无sudo配置
    if _, err := json_data.Get("result").Array(); err == nil {
        return "empty", nil
    }

    // 返回string
    sudo, err := json_data.Get("result").String()
    if err != nil {
        return "", errors.New("result not string or list error")
    }
    return sudo, nil
}
