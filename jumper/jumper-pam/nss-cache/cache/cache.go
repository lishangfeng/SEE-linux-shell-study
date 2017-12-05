package cache

import (
    "time"
    "encoding/json"
    "jumper-pam/nss-cache/lib"
    "jumper-pam/nss-cache/conf"
    "jumper-pam/nss-cache/model"
    "github.com/thevipwan/go-logger/logger"
)

var (
    Version string
    LastNssTime time.Time
)

func init() {
    cache_data, cache_version := lib.NssLoad()
    Version = string(cache_version)
    json.Unmarshal(cache_data, &model.NssIndexId)
    for i, _ := range model.NssIndexId {
        model.NssIndexName[model.NssIndexId[i].Name] = model.NssIndexId[i]
    }
}

func NssCache() {
    for {
        nss_data, err := lib.FetchNss(Version);
        if nss_data.Result.Version == "" {
            logger.Error("[nss-cache] 从服务端获取数据失败, 版本号丢失, 请核对结构体")
            lib.RandSleep(conf.Config.Get("cache_random", "1200").(string))
            continue
        } else {
            LastNssTime = time.Now()
        }

        if err != nil {
            logger.Info("[nss-cache] 从服务端获取数据失败")
            lib.RandSleep(conf.Config.Get("cache_random", "1200").(string))
            continue
        }
        if Version == nss_data.Result.Version {
            logger.Info("[nss-cache] 本地已经是最新版本, 无需更新:", Version)
            lib.RandSleep(conf.Config.Get("cache_random", "1200").(string))
            continue
        } else {
            Version = nss_data.Result.Version
        }

        for _, user := range nss_data.Result.User {
            var user_info model.UserInfo
            user_info.Groups = make(map[int]string)
            user_info.ID = user.Pw_Uid
            user_info.Name = user.Pw_name
            user_info.Type = "user"
            for _, group := range user.Group {
                user_info.Groups[group.Gr_gid] = group.Gr_name
            }
            model.NssSet(&user_info)
            logger.Info("[nss-cache] 更新 nss-user:", user_info.Name)
        }

        for _, group := range nss_data.Result.Group {
            var group_info model.UserInfo
            group_info.ID = group.Gr_gid
            group_info.Name = group.Gr_name
            group_info.Type = "group"
            for _, user := range group.Gr_mem {
                group_info.Members = append(group_info.Members, user)
            }
            model.NssSet(&group_info)
            logger.Info("[nss-cache] 更新 nss-group:", group_info.Name)
        }

        for _, name := range nss_data.Result.Delete {
            _, ok := model.NssIndexName[name]
            if ok == true {
                user_info := *model.NssIndexName[name]
                delete(model.NssIndexName, name)
                nameId := user_info.ID
                _, ok := model.NssIndexName[name]
                if ok == true{
                    delete(model.NssIndexId, nameId)
                }
            }
            logger.Info("[nss-cache] 删除", name)
        }
        logger.Info("更新完成, 当前版本 ", Version)
        lib.RandSleep(conf.Config.Get("cache_random", "1200").(string))
    }
}
