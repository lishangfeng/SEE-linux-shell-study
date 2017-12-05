#!/bin/env python
# -*- coding:utf-8 -*-

import time
import json
from datetime import timedelta
from datetime import datetime
from sqlalchemy import func, desc


from flask import current_app as app
from app.models import *
from app.lib.database import db


def get_top_user(interval=7):
    start_day = datetime.now() - timedelta(days=interval)
    query_field = db.session.query(LoginHistory.user_name, func.count('*').label("user_count"))
    query_range = query_field.filter(LoginHistory.login_time >= start_day)
    query_group_by = query_range.group_by(LoginHistory.user_name)
    query_order_by = query_group_by.order_by(desc(func.count('*').label("user_count")))
    top_users = query_order_by.limit(10).all()
    return top_users
