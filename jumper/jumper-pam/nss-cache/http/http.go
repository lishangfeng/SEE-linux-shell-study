package http

import (
    "log"
    "strings"
    "strconv"
    "net/http"
    "io/ioutil"
    "encoding/json"
    "jumper-pam/nss-cache/conf"
    "jumper-pam/nss-cache/lib"
    "jumper-pam/nss-cache/model"
    "github.com/thevipwan/go-logger/logger"
)

type Result struct {
    Msg  string         `json:"msg"`
    Code int            `json:"code"`
    Data interface{}    `json:"data"`
}

type Req struct {
    Cache_Random  string
    Remote_Access string
}

func init() {

    http.HandleFunc("/", func(w http.ResponseWriter, req *http.Request) {
        if req.Method == "GET" {
            renderDataJson(w, GatherInfo(), 200)
        } else {
            http.Error(w, "Sorry, only GET method are supported.", http.StatusMethodNotAllowed)
        }
    })
    http.HandleFunc("/config", func(w http.ResponseWriter, req *http.Request) {
        switch req.Method {
        case "GET":
            renderDataJson(w, conf.Config, 200)
        case "POST":
            remote_addr := strings.Split(req.RemoteAddr, ":")[0]
            ip_whitelist := conf.Config.Get("ip_whitelist").(map[string]string)
            if !lib.StringInMap(remote_addr, ip_whitelist) {
                renderDataJson(w, "您的IP不在访问白名单!", 205)
                logger.Info("[http-server] (/config)客户端请求IP不在白名单: ", remote_addr)
                return
            }
            var request_data Req
            body, _ := ioutil.ReadAll(req.Body)
            err := json.Unmarshal(body, &request_data)
            if err != nil {
                logger.Warn("[http-server] 请求体错误: " + string(body))
                renderDataJson(w, "请数据格式不正确!", 205)
                return
            }
            if request_data.Remote_Access != "" {
                type_auth := map[string]string{
                    "1": "1",
                    "2": "2",
                    "3": "3",
                }
                if lib.StringInMap(request_data.Remote_Access, type_auth) {
                    logger.Info("[http-server] 更新配置 remote_access: ", request_data.Remote_Access)
                    conf.Config.Set("remote_access", request_data.Remote_Access)
                } else {
                    logger.Warn("[http-server] 请求配置值不合法 remote_access: ", request_data.Remote_Access)
                }
            }
            if request_data.Cache_Random != "" {
                if _, err := strconv.Atoi(request_data.Cache_Random); err == nil {
                    logger.Info("[http-server] 更新配置 cache_random: ", request_data.Cache_Random)
                    conf.Config.Set("cache_random", request_data.Cache_Random)
                } else {
                    logger.Warn("[http-server] 配置值不合法，非数字型 cache_random: ", request_data.Cache_Random)
                }
            }
            renderDataJson(w, conf.Config, 200)
        default:
            logger.Info("[http-server] (/config)客户端请求方法不对: ", req.Method)
            http.Error(w, "Sorry, only GET and POST methods are supported.", http.StatusMethodNotAllowed)
        }
    })
    http.HandleFunc("/nss", func(w http.ResponseWriter, req *http.Request) {
        switch req.Method {
        case "GET":
            query := req.URL.Query()
            if len(query) != 1 {
                msg := "请求参数不正确!  uid, gid, user_name, group_name 其中之一"
                renderDataJson(w, msg, 205)
                return
            }
            if query.Get("uid") != "" {
                renderDataJson(w, model.NssGet(query.Get("uid"), "user", "id"), 200)
                logger.Info("[http-server] 查询uid: ", query.Get("uid"))
                return
            } else if query.Get("user_name") != "" {
                renderDataJson(w, model.NssGet(query.Get("user_name"), "user", "name"), 200)
                logger.Info("[http-server] 查询user_name: ", query.Get("user_name"))
                return
            } else if query.Get("gid") != "" {
                renderDataJson(w, model.NssGet(query.Get("gid"), "group", "id"), 200)
                logger.Info("[http-server] 查询gid: ", query.Get("gid"))
                return
            } else if query.Get("group_name") != "" {
                renderDataJson(w, model.NssGet(query.Get("group_name"), "group", "name"), 200)
                logger.Info("[http-server] 查询group_name: ", query.Get("group_name"))
                return
            }
        default:
            logger.Info("[http-server] (/nss)客户端请求方法不对: ", req.Method)
            http.Error(w, "Sorry, only GET method are supported.", http.StatusMethodNotAllowed)
        }
    })
}

func renderJson(w http.ResponseWriter, v interface{}) {
    bs, err := json.MarshalIndent(v, "", "\t")
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    w.Header().Set("Content-Type", "application/json; charset=UTF-8")
    w.Write(bs)
}

func renderDataJson(w http.ResponseWriter, data interface{}, code int) {
    renderJson(w, Result{Msg: "操作成功", Data: data, Code: code})
}

func HttpServer() {
    log.Println("开启httpserver: ", conf.Config.Get("listen", "0.0.0.0:7888").(string))
    err := http.ListenAndServe(conf.Config.Get("listen", "0.0.0.0:7888").(string), nil)
    if err != nil {
        log.Fatal("开启httpserver失败: ", err)
    }
}
