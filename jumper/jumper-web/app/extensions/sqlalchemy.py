# -*- coding: utf-8 -*-

from app.lib.error_define import SQLAlchemyError
from flask import current_app as app

from types import MethodType
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

def wrapper(method):
    @wraps(method)
    def wrapped(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception as e:
            msg = 'function[{0}] occurred error --> {1}'.format(method.__name__, str(e))
            app.logger.warning(msg)
            raise SQLAlchemyError(msg)
    return wrapped


# class NewSQLAlchemy(SQLAlchemy):
#     def init_app(self, app):
#         super(NewSQLAlchemy, self).init_app(app)
#         self.create_all()
#         attr = super(SQLAlchemy, self).__getattribute__()
#         if type(attr) == MethodType:
#             attr = wrapper(attr)
#         return attr


class NewSQLAlchemy(SQLAlchemy):
    def init_app(self, app):
        super(NewSQLAlchemy, self).init_app(app)
        # self.create_all()

extension = NewSQLAlchemy()
