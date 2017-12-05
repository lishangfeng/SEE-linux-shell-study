package lib

import (
    "fmt"
    "strconv"
    "time"
    "math/rand"
    "io/ioutil"
    "os"
    "net"
    "os/exec"
    "strings"
    "github.com/thevipwan/go-logger/logger"
)

func NssPack(send_data []byte) []byte {
    logger.Debug("send: ", string(send_data))
    return []byte(fmt.Sprintf("%016d%s", len(send_data), string(send_data)))
}

func WritePid(pid_file string) {
    ioutil.WriteFile(pid_file, []byte(strconv.Itoa(os.Getpid())), 0644)
}

func RandSleep(rand_time string) {
    cache_random, _ := strconv.Atoi(rand_time)
    if cache_random < 600 {
        time.Sleep(time.Duration(600) * time.Second)
    } else {
        rand.Seed(time.Now().UnixNano())
        random := rand.Intn(600)
        time.Sleep(time.Duration(cache_random-random) * time.Second)
    }
}

func HostInfo() (hostname, ip string) {
    ip = "127.0.0.1"
    hostname, _ = os.Hostname()
    ips, err := net.LookupIP(hostname)

    // 判断ip是否为本地回环地址
    if err == nil {
        ipv4 := ips[0].To4()
        if ipv4.IsLoopback() == false {
            ip = ipv4.String()
            return
        }
    }

    dns_command := fmt.Sprintf("host %s |grep \"has address\"|head -n1|awk '{print $NF}'", hostname)
    output, _ := exec.Command("bash", "-c", dns_command).Output()
    temp := strings.TrimSpace(string(output))
    if len(temp) > 0 {
        ip = temp
        return
    } else {
        // CentOS 6.x first interface ip
        centos6 := "/sbin/ifconfig | grep \"Mask\" | head -n1| awk -F'[ :]+' '{print $4}'"
        output, _ := exec.Command("bash", "-c", centos6).Output()
        temp := strings.TrimSpace(string(output))
        if len(temp) > 0 {
            ip = temp
            return
        } else {
            // CentOS 7.x first interface ip
            centos7 := "/sbin/ifconfig | grep \"netmask\"|head -n1|awk  '{print $2}'"
            output, _ := exec.Command("bash", "-c", centos7).Output()
            temp := strings.TrimSpace(string(output))
            if len(temp) > 0 {
                ip = temp
                return
            }
        }
    }
    return
}

func StringInMap(a string, list map[string]string) bool {
    for _, b := range list {
        if b == a {
            return true
        }
    }
    return false
}
