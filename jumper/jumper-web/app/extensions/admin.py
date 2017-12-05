# -*- coding: utf-8 -*-

from flask import current_app as app
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app.models import *


def list_models(db):
    classes, models, table_names = [], [], []
    for clazz in db.Model._decl_class_registry.values():
        try:
            table_names.append(clazz.__tablename__)
            classes.append(clazz)
        except:
            pass

    for table in db.metadata.tables.items():
        if table[0] in table_names:
            models.append(classes[table_names.index(table[0])])

    return models


if app.config.get('APP_ENV') in ['beta', 'ppe', 'qa']:
    extension = Admin(name='app', template_mode='bootstrap3')
    for model in list_models(db):
        extension.add_view(ModelView(model, db.session))
