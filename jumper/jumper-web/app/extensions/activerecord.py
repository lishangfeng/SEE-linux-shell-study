# -*- coding: utf-8 -*-

from flask_activerecord import patch_model


class Ext(object):
    def __init__(self):
        pass

    def init_app(self, app):
        patch_model()

extension = Ext()
