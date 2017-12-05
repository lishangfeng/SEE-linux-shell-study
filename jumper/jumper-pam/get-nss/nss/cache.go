package nss

import (
    "path"
    "strconv"
    "io/ioutil"
    "encoding/json"
    "jumper-pam/nss-cache/lib"
    "jumper-pam/nss-cache/conf"
    "jumper-pam/nss-cache/model"
    "github.com/thevipwan/go-logger/logger"
)

func NssCache() {
    logger.Info("[get-nss] 开始把缓存数据写到磁盘")
    cache_dir := conf.Config.Get("cache_dir", "/var/lib/nss-cache").(string)
    var password_cache = make(map[string]interface{})
    var group_cache = make(map[string]interface{})
    var group_all_cache []interface{}
    nss_data, err := lib.FetchNss("xxxx")

    if err != nil {
        logger.Info("[get-nss] 从服务端获取数据失败")
        return
    }
    Version := nss_data.Result.Version

    for _, user := range nss_data.Result.User {
        if user.Pw_name == "" {
            continue // 忽略无用户名的垃圾组
        }
        var user_info model.UserInfo
        user_info.Groups = make(map[int]string)
        user_info.ID = user.Pw_Uid
        user_info.Name = user.Pw_name
        user_info.Type = "user"
        for _, group := range user.Group {
            user_info.Groups[group.Gr_gid] = group.Gr_name
        }
        origin := user_info.OriginPassword()
        user_group := user_info.OriginGroup()
        password_cache[user_info.Name] = origin
        password_cache[strconv.Itoa(user_info.ID)] = origin
        group_cache[user_info.Name] = user_group
        group_cache[strconv.Itoa(user_info.ID)] = user_group
        group_all_cache = append(group_all_cache, user_group)
        model.NssSet(&user_info)
    }

    for _, group := range nss_data.Result.Group {
        if len(group.Gr_mem) == 0 {
            continue // 忽略没有member的组，fix group_all 无效问题
        }
        var group_info model.UserInfo
        group_info.ID = group.Gr_gid
        group_info.Name = group.Gr_name
        group_info.Type = "group"
        for _, user := range group.Gr_mem {
            group_info.Members = append(group_info.Members, user)
        }
        origin := group_info.OriginGroup()
        group_cache[strconv.Itoa(group_info.ID)] = origin
        group_cache[group_info.Name] = origin
        group_all_cache = append(group_all_cache, origin)
        model.NssSet(&group_info)
    }

    group, _ := json.Marshal(group_cache)
    passwd, _ := json.Marshal(password_cache)
    group_all, _ := json.Marshal(group_all_cache)

    nss_cache, _ := json.Marshal(model.NssIndexId)
    ioutil.WriteFile(path.Join(cache_dir, "version"), []byte(Version), 0644)
    ioutil.WriteFile(path.Join(cache_dir, "cache.db"), nss_cache, 0644)
    ioutil.WriteFile(path.Join(cache_dir, "passwd"), passwd, 0644)
    ioutil.WriteFile(path.Join(cache_dir, "group"), group, 0644)
    ioutil.WriteFile(path.Join(cache_dir, "group_all"), group_all, 0644)
    logger.Info("[get-nss] 缓存写入磁盘完成")
    return
}
