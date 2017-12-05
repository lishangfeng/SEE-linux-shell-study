package main

import (
    "os"
    "syscall"
    "fmt"
)

func Alex()  {
    fmt.Println("hah")
}
/* 测试文件Dev,Ino判断文件是否一样 */
func main(){
    filename := "a.txt"
    fileinfo, _ := os.Stat(filename)
    stat := fileinfo.Sys().(*syscall.Stat_t)
    fmt.Println(stat.Dev)
    fmt.Println(stat.Ino)
}