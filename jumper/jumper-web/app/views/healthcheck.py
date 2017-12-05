# -*- coding: utf-8 -*-

from flask import current_app as app
from app.extensions.sqlalchemy import extension as db
from app.lib.error_define import res
from app.lib.app_redis import Rds


def check_db():
    try:
        db.session.execute('SELECT 1')
        status = True
    except Exception as e:
        status = str(e)
    return status


def check_redis():
    Rds.router().time()
    return True


@app.route('/api/healthcheck')
def healthcheck():
    db_status = check_db()
    check_redis()
    if db_status is True:
        return res(code=200, msg='ok')
    return res(code=206, msg=db_status)
