package model

import (
    "encoding/json"
    "strconv"
    "sync"
)

type UserInfo struct {
    ID      int
    Name    string
    Type    string
    Groups  map[int]string
    Members []string
}

var (
    mutex sync.RWMutex
    NssIndexName map[string]*UserInfo
    NssIndexId   map[int]*UserInfo
)

func init() {
    NssIndexName = make(map[string]*UserInfo)
    NssIndexId = make(map[int]*UserInfo)
}

func NssSet(user_info *UserInfo) {
    mutex.Lock()
    defer mutex.Unlock()
    NssIndexName[user_info.Name] = user_info
    NssIndexId[user_info.ID] = user_info
}

func NssGetId(id string) UserInfo {
    id_int, _ := strconv.Atoi(id)
    user_info, ok := NssIndexId[id_int]
    if ok == true {
        return *user_info
    } else {
        return UserInfo{}
    }
}

func NssGetName(name string) UserInfo {
    user_info, ok := NssIndexName[name]
    if ok == true {
        return *user_info
    } else {
        return UserInfo{}
    }
}

func (user_info UserInfo) Shadow() []byte {
    if user_info.Name == ""{
        return []byte(`{}`)
    }
    shadow := make(map[string]interface{})
    shadow["sp_namp"] = user_info.Name
    shadow["sp_pwdp"] = "xx-xx-xx-xx"
    shadow["sp_lstchg"] = 16034
    shadow["sp_min"] = 0
    shadow["sp_max"] = 99999
    shadow["sp_warn"] = 7
    shadow["sp_inact"] = ""
    shadow["sp_expire"] = ""
    shadow["sp_flag"] = ""
    data, _ := json.Marshal(shadow)
    return data
}

func (user_info UserInfo) Password() []byte {
    if user_info.Name == ""{
        return []byte(`{}`)
    }
    password := make(map[string]interface{})
    password["pw_dir"] = "/home/" + user_info.Name
    password["pw_name"] = user_info.Name
    password["pw_shell"] = "/bin/bash"
    password["pw_uid"] = user_info.ID
    data, _ := json.Marshal(password)
    return data
}

func (user_info UserInfo) OriginPassword() interface{} {
    if user_info.Name == ""{
        return []byte(`{}`)
    }
    password := make(map[string]interface{})
    password["pw_dir"] = "/home/" + user_info.Name
    password["pw_name"] = user_info.Name
    password["pw_shell"] = "/bin/bash"
    password["pw_uid"] = user_info.ID
    return password
}

func (user_info UserInfo) OriginGroup() interface{} {
    if user_info.Name == ""{
        return []byte(`{}`)
    }
    group_info := make(map[string]interface{})
    group_info["gr_gid"] = user_info.ID
    group_info["gr_name"] = user_info.Name
    if user_info.Type == "group" {
        group_info["gr_mem"] = user_info.Members
    } else {
        group_info["gr_mem"] = []string{user_info.Name}
    }
    return group_info
}

func (user_info UserInfo) UserGroup() []byte {
    if user_info.Name == ""{
        return []byte(`{}`)
    }
    var group_list []map[string]interface{}
    for gid, group_name := range user_info.Groups {
        group_info := make(map[string]interface{})
        group_info["gr_name"] = group_name
        group_info["gr_gid"] = gid
        group_info["gr_mem"] = []string{user_info.Name}
        group_list = append(group_list, group_info)
    }
    data, _ := json.Marshal(group_list)
    return data
}

func (user_info UserInfo) UserGroupById(gid string) []byte {
    if user_info.Name == ""{
        return []byte(`{}`)
    }
    gid_int, _ := strconv.Atoi(gid)
    group_name, ok := user_info.Groups[gid_int]
    if ok == true {
        group_info := make(map[string]interface{})
        group_info["gr_name"] = group_name
        group_info["gr_gid"], _ = strconv.Atoi(gid)
        group_info["gr_mem"] = []string{user_info.Name}
        data, _ := json.Marshal(group_info)
        return data
    } else {
        return []byte(`{}`)
    }
}

func (user_info UserInfo) Group() []byte {
    if user_info.Name == ""{
        return []byte(`{}`)
    }
    group_info := make(map[string]interface{})
    group_info["gr_gid"] = user_info.ID
    group_info["gr_name"] = user_info.Name
    if user_info.Type == "group" {
        group_info["gr_mem"] = user_info.Members
    } else {
        group_info["gr_mem"] = []string{user_info.Name}
    }
    data, _ := json.Marshal(group_info)
    return data
}
