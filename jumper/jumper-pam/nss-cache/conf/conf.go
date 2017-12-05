package conf

import (
    "io"
    "os"
    "sync"
    "bufio"
    "strings"
    "github.com/larspensjo/config"
    "github.com/thevipwan/go-logger/logger"
)

type Conf map[string]interface{}

var (
    conf_mutex sync.RWMutex
    Config Conf = make(Conf, 20)
    configFile string = "/etc/nss-http.conf"
    //configFile string = "/Users/xk/Desktop/nss-http.conf"
)

func init() {
    ParseConfig()
    LoadLocalAccount()
}

func LoadLocalAccount() map[string]string {
    var black_list = make(map[string]string, 20)
    for _, filename := range []string{"/etc/passwd", "/etc/group"} {
        fi, err := os.Open(filename)
        if err != nil {
            logger.Error("[nss-conf]: 加载本地用户黑名单失败", err)
            return black_list
        }
        defer fi.Close()
        br := bufio.NewReader(fi)
        for {
            a, _, c := br.ReadLine()
            if c == io.EOF {
                break
            }
            if strings.HasPrefix(string(a), "#") {
                continue
            } else {
                user := strings.Split(string(a), ":")
                if user[0] != ""{
                    black_list[user[0]] = user[0]
                }
            }
        }
    }
    return black_list
}

func (config *Conf) Get(name string, args ...interface{}) interface{} {
    conf_mutex.RLock()
    defer conf_mutex.RUnlock()
    if key, ok := (*config)[name]; ok {
        return key
    } else if len(args) >= 1 {
        return args[0]
    } else {
        return key
    }
}

func (config *Conf) Set(name string, value interface{}) interface{} {
    conf_mutex.Lock()
    defer conf_mutex.Unlock()
    (*config)[name] = value
    return value
}

func ParseConfig() {
    cfg, err := config.ReadDefault(configFile)
    if err != nil {
        logger.Error("Fail to find", configFile, err.Error())
        os.Exit(1)
    }

    //Initialized topic from the configuration
    if cfg.HasSection("sudo") {
        section, err := cfg.SectionOptions("sudo")
        if err == nil {
            for _, v := range section {
                options, err := cfg.String("sudo", v)
                if err == nil {
                    //Config[v] = options
                    Config.Set(v, options)
                }
            }
        }
    }

    if cfg.HasSection("cache") {
        section, err := cfg.SectionOptions("cache")
        if err == nil {
            for _, v := range section {
                options, err := cfg.String("cache", v)
                if err == nil {
                    //Config[v] = options
                    Config.Set(v, options)
                }
            }
        }


        // 加载用户和组黑名单
        local_user := LoadLocalAccount()
        user_blacklist := strings.Split(Config.Get("user_blacklist", "root").(string), ",")
        for _, i := range user_blacklist{
            local_user[strings.TrimSpace(i)] = strings.TrimSpace(i)
        }
        local_user["c"] = "c"   // 服务器上sudo携带的未知组
        Config.Set("user_blacklist", local_user)

        // 加载ip白名单
        var ip = make(map[string]string, 10)
        ip_whitelist := strings.Split(Config.Get("ip_whitelist", "127.0.0.1").(string), ",")
        for _, i := range ip_whitelist{
            ip[strings.TrimSpace(i)] = strings.TrimSpace(i)
        }
        Config.Set("ip_whitelist", ip)
    }
}
