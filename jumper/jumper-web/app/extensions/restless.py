# -*- coding: utf-8 -*-

from flask_restless import APIManager

from app.lib.database import db


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


extension = APIManager(flask_sqlalchemy_db=db)
for model in list_models(db):
    extension.create_api(model, methods=['GET', 'POST', 'DELETE'], url_prefix='/api/v0')
