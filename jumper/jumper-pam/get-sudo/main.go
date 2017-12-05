package main

import (
    "jumper-pam/get-sudo/sudo"
    "jumper-pam/nss-cache/lib"
)

func init() {
    lib.InitLogger()
}

func main() {
    sudo.SudoCache()
}
