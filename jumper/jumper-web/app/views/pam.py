#!/bin/env python
# -*- coding:utf-8 -*-

from app.pam.auth import AccountCheck
from app.lib.view_decorator import ViewDecorator


@ViewDecorator('/pam/account', methods=['GET'])
def pam_account(data):
    return AccountCheck(data).check_account()


@ViewDecorator('/pam/password', methods=['POST'])
def pam_password(data):
    return AccountCheck(data).check_password()
