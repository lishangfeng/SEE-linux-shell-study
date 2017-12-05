package model

import (
    "strconv"
    "jumper-pam/nss-cache/lib"
    "github.com/thevipwan/go-logger/logger"
    "jumper-pam/nss-cache/conf"
)

func NssGetCache(key string, role string, _type string, process_name string) (user_info UserInfo) {
    if conf.Config.Get("remote_access", "3").(string) == "1"{           // 本地缓存
        user_info = NssGet(key, role, _type)
    } else if conf.Config.Get("remote_access", "3").(string) == "2" {   // 远程缓存
        user_info = NssGetServer(key, role, _type)
    } else if conf.Config.Get("remote_access", "3").(string) == "3" {   // 先取本地，本地无再取远程
        user_info = NssGet(key, role, _type)
        if user_info.Name == ""{
            if process_name != "sshd"{
                logger.Debug("未命中本地缓存，非登录进程查询，不取远程", role, _type, key, process_name)
            } else {
                logger.Warn("未命中本地缓存，sshd进程，尝试从服务端获取", role, _type, key)
                user_info = NssGetServer(key, role, _type)
            }
        }
    }
    return
}


func NssGet(key string, role string, _type string) (user_info UserInfo) {
    if _type == "id" {
        id, _ := strconv.Atoi(key)
        mutex.RLock()
        _, ok := NssIndexId[id]
        if ok == true {
            user_info = *NssIndexId[id]
        }
        mutex.RUnlock()
    } else {
        mutex.RLock()
        _, ok := NssIndexName[key]
        if ok == true {
            user_info = *NssIndexName[key]
        }
        mutex.RUnlock()
    }

    /*
        避免用户查询, 命中组信息
        getent passwd dp_op     不命中
        getent group alex.wan   命中
    */
    if user_info.Name != "" {
        if role == "group"{
            return
        } else if user_info.Type == "user" {
            return
        } else {
            user_info = UserInfo{}
        }
    }
    return
}

func NssGetServer(key string, role string, _type string) (user_info UserInfo) {
    /* 缓存未命中, 尝试从服务端查询信息 */

    /* 黑名单用户 */
    user_blacklist := conf.Config.Get("user_blacklist").(map[string]string)
    if _type == "name" && lib.StringInMap(key, user_blacklist){
        logger.Debug("本地黑名单账号", role, _type, key)
        return
    }

    if role == "user" {
        nss_user, err := lib.FetchNssUser(key, _type)
        if err != nil {
            logger.Info("从服务端获取失败", err.Error())
            return
        } else {
            user_info.Groups = make(map[int]string)
            user_info.ID = nss_user.Result.Pw_Uid
            user_info.Name = nss_user.Result.Pw_name
            user_info.Type = "user"
            for _, group := range nss_user.Result.Group {
                user_info.Groups[group.Gr_gid] = group.Gr_name
            }
        }
    } else {
        nss_group, err := lib.FetchNssGroup(key, _type)
        if err != nil {
            logger.Info("从服务端获取失败", err.Error())
            return
        } else {
            user_info.ID = nss_group.Result.Gr_gid
            user_info.Name = nss_group.Result.Gr_name
            user_info.Type = "group"
            for _, user := range nss_group.Result.Gr_mem {
                user_info.Members = append(user_info.Members, user)
            }
        }
    }
    NssSet(&user_info)
    return
}
