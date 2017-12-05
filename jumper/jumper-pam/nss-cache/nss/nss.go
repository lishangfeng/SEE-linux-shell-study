package nss

import (
    "os"
    "net"
    "encoding/json"
    "github.com/thevipwan/go-logger/logger"
    "jumper-pam/nss-cache/model"
    "jumper-pam/nss-cache/lib"
    "jumper-pam/nss-cache/conf"
)

func nss(socket net.Conn) {
    defer socket.Close()

    var user_info model.UserInfo
    user_info.Groups = make(map[int]string)
    data := make([]byte, 10240)
    result := make(map[string]string)

    for {
        n, err := socket.Read(data)
        if err != nil {
            logger.Debug("socket.Read EOF :", err.Error())
            return
        }
        if n == 0 {
            return
        }

        logger.Debug("recv: ", string(data[0:n]))
        err = json.Unmarshal(data[0:n], &result)
        if err != nil {
            logger.Info("数据格式不对，非json", err.Error())
            return
        }

        if result["type"] == "password" {
            if result["name"] == "uid" {
                user_info = model.NssGetCache(result["value"], "user", "id", result["process_name"])
            } else if result["name"] == "name" {
                user_info = model.NssGetCache(result["value"], "user", "name", result["process_name"])
            }
            socket.Write(lib.NssPack(user_info.Password()))
        } else if result["type"] == "shadow" {
            socket.Write(lib.NssPack(user_info.Shadow()))
        } else if result["type"] == "group" {
            if result["name"] == "gid" {
                if user_info.Type == "user" {
                    socket.Write(lib.NssPack(user_info.UserGroupById(result["value"])))
                } else {
                    user_info = model.NssGetCache(result["value"], "group", "id", result["process_name"])
                    socket.Write(lib.NssPack(user_info.Group()))
                }
            } else if result["name"] == "name" {
                user_info = model.NssGetCache(result["value"], "group", "name", result["process_name"])
                socket.Write(lib.NssPack(user_info.Group()))
            } else {
                socket.Write(lib.NssPack(user_info.UserGroup()))
            }
        } else {
            return
        }
    }
}

func SocketServer() {
    //listener, err := net.Listen("tcp", "0.0.0.0:8888")
    SockPath := conf.Config.Get("sock_path", "/var/run/nss-cache.sock").(string)
    os.Remove(SockPath)
    listener, err := net.Listen("unix", SockPath)
    os.Chmod(SockPath, 00777)

    if err != nil {
        logger.Error("监听unix文件失败", err.Error())
        os.Exit(1)
    }
    defer listener.Close()
    logger.Info("开始监听Socket: ", SockPath)

    for {
        conn, err := listener.Accept()
        if err != nil {
            logger.Error("Error socket.accept:", err.Error())
            continue
        } else {
            go nss(conn)
        }
    }
}
