# !/bin/env python
# -*- coding:utf-8 -*-

import string
import hashlib
from random import sample
from base64 import urlsafe_b64decode as decode
from base64 import urlsafe_b64encode as encode


class Password:
    salt_length = 8
    random_pass_length = 16

    def __init__(self):
        pass

    @classmethod
    def get_salt(cls):
        salt_seed = string.digits + string.ascii_letters + string.punctuation
        return ''.join(sample(salt_seed, cls.salt_length))

    @classmethod
    def random_password(cls):
        password_seed = string.digits + string.ascii_letters + string.punctuation
        password_normal = string.digits + string.ascii_letters
        password_string = ''.join(sample(password_seed, cls.random_pass_length - 2))
        first_last = sample(password_normal, 2)
        return first_last[0] + password_string + first_last[1]

    @classmethod
    def get_password128(cls, password=None, salt=None):
        salt = str((salt or cls.get_salt()))
        password = str((password or cls.random_password()))
        if isinstance(password, str) or isinstance(password, unicode):
            hr = hashlib.sha1(password)
            hr.update(salt)
            return "{SSHA}" + encode(hr.digest() + salt), salt

    @classmethod
    def get_password(cls, password=None, salt=None):
        salt = str((salt or cls.get_salt()))
        password = str((password or cls.random_password()))
        if isinstance(password, str) or isinstance(password, unicode):
            hr = hashlib.sha512(password)
            hr.update(salt)
            return "{SSHA}" + encode(hr.digest() + salt), salt

    @classmethod
    def check_password(cls, challenge_password, password):
        checked = False
        if len(challenge_password) == 102:
            checked = cls.check_password_sha512(challenge_password, password)
        elif len(challenge_password) == 46:
            checked = cls.check_password_sha128(challenge_password, password)
        return checked

    @staticmethod
    def check_password_sha128(challenge_password, password):
        challenge_password = str(challenge_password)
        password = str(password)
        challenge_bytes = decode(challenge_password[6:])
        digest = challenge_bytes[:20]
        salt = challenge_bytes[20:]
        hr = hashlib.sha1(password)
        hr.update(salt)
        return digest == hr.digest()

    @staticmethod
    def check_password_sha512(challenge_password, password):
        challenge_password = str(challenge_password)
        password = str(password)
        challenge_bytes = decode(challenge_password[6:])
        digest = challenge_bytes[:64]
        salt = challenge_bytes[64:]
        hr = hashlib.sha512(password)
        hr.update(salt)
        return digest == hr.digest()
