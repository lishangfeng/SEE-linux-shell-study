# -*- coding:utf-8 -*-

from app.lib.app_redis import Rds
from app.lib.view_decorator import ViewDecorator


@ViewDecorator('/repair.sh', response=False)
def get_script(data):
    script = Rds.router().get("repair_jumper")
    if not script:
        return u"echo 未找到脚本"
    return script


@ViewDecorator('/repair.sh', methods=['POST'])
def save_script(data):
    script = data['post'].get("script")
    if script:
        return Rds.router().set("repair_jumper", script)


@ViewDecorator('/repair.sh', methods=['DELETE'])
def delete_script(data):
    return Rds.router().delete("repair_jumper")
