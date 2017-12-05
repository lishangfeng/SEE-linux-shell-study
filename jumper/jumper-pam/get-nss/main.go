package main

import (
    "jumper-pam/nss-cache/lib"
    "jumper-pam/get-nss/nss"
)

func init() {
    lib.InitLogger()
}

func main() {
    nss.NssCache()
}
