#!/bin/env python
# -*- coding:utf-8 -*-

from flask import current_app as app

from app.lib.database import db
from app.lib.error_define import SQLAlchemyError
from app.lib.error_define import SupportError
from sqlalchemy.inspection import inspect


class RestfulGet:
    def __init__(self, module, data):
        self.module = module
        self.data = data
        self.keys = self.module.get_keys()

        self.show = [k for k in self.data.get('show', '').split(',') if k in self.keys]
        self.page_size = int(self.data.get('page_size', app.config.get('PAGE_SIZE', 25)))
        self.page = int(self.data.get('page', 1))
        self.result = dict(num_results=0, total_pages=1, page=self.page, page_size=self.page_size, objects=list())

        self.query = self.get_query()
        self.query_conditions = list()

        self.get_query_conditions()
        self.filter()
        self.order_by()
        self.limit()
        self.filter_row()

    def get_query(self):
        if self.show:
            return db.session.query(*[getattr(self.module, k) for k in self.show])
        else:
            return db.session.query(self.module)

    def get_query_conditions(self):
        for k, v in self.data.items():
            if k in ['show', 'order_by', 'page_size', 'page']:
                continue
            elif '<' in k:
                self.query_conditions.append(dict(
                    name=k.split('<')[-1],
                    op='<',
                    val=v
                ))
            elif '>' in k:
                self.query_conditions.append(dict(
                    name=k.split('>')[-1],
                    op='>',
                    val=v
                ))
            elif '@' in k:
                self.query_conditions.append(dict(
                    name=k.split('@')[-1],
                    op='@',
                    val=v
                ))
            elif '^' in k:
                self.query_conditions.append(dict(
                    name=k.split('^')[-1],
                    op='^',
                    val=v
                ))
            elif '$' in k:
                self.query_conditions.append(dict(
                    name=k.split('$')[-1],
                    op='$',
                    val=v
                ))
            else:
                self.query_conditions.append(dict(
                    name=k,
                    op='=',
                    val=v
                ))

    def filter(self):
        for data in self.query_conditions:
            if not data['val'] or not data['name'] or data['name'] not in self.keys:
                continue
            elif data['op'] == '<':
                self.query = self.query.filter(getattr(self.module, data['name']) < data['val'])
            elif data['op'] == '>':
                self.query = self.query.filter(getattr(self.module, data['name']) > data['val'])
            elif data['op'] == '@':
                self.query = self.query.filter(getattr(self.module, data['name']).like('%{0}%'.format(data['val'])))
            elif data['op'] == '^':
                self.query = self.query.filter(getattr(self.module, data['name']).like('{0}%'.format(data['val'])))
            elif data['op'] == '$':
                self.query = self.query.filter(getattr(self.module, data['name']).like('%{0}'.format(data['val'])))
            else:
                self.query = self.query.filter(getattr(self.module, data['name']) == data['val'])

    def order_by(self):
        for k in self.data.get('order_by', '').split(','):
            if not k or k not in self.keys:
                continue
            self.query = self.query.order_by(-getattr(self.module, k))

    def limit(self):
        if self.page_size > 2000:
            self.page_size = self.result['page_size'] = 2000
        if inspect(self.module).primary_key:
            self.result['num_results'] = self.query.with_entities(inspect(self.module).primary_key[0]).count()
        else:
            self.result['num_results'] = self.query.count()
        self.result['total_pages'], n = divmod(self.result['num_results'], self.page_size)
        if n:
            self.result['total_pages'] += 1
        self.query = self.query.offset((self.page - 1) * self.page_size).limit(self.page_size)

    def filter_row(self):
        if not self.show:
            self.result['objects'] = [data.to_dict() for data in self.query]
        else:
            for i in self.query:
                data = dict()
                for k in self.keys:
                    if hasattr(i, k):
                        data[k] = getattr(i, k)
                else:
                    self.result['objects'].append(data)


class RestfulPut:
    def __init__(self, module, _id, request_data):
        self.request = request_data
        self.id = _id
        self.primary_key = inspect(module).primary_key[0].name
        self.module = module
        self.query = db.session.query(self.module).filter(getattr(self.module, self.primary_key) == self.id)
        self.k = [k for k in dir(module)
                  if k not in ['metadata', 'query', 'query_class', 'to_dict'] and not k.startswith("_")]

        self.filter()
        self.result = self.process()

    def filter(self):
        for k, _ in self.request.items():
            if k not in self.k:
                del self.request[k]

    def process(self):
        try:
            self.query.update(self.request)
            db.session.commit()
            result = db.session.query(self.module).filter(getattr(self.module, self.primary_key) == self.id).first()
            return result.to_dict() if result else u"{0}={1} 不存在, 忽略更新.".format(self.primary_key, self.id)
        except Exception as e:
            app.logger.error(u'更新DB失败: {0}'.format(str(e)))
            raise SupportError(u'更新DB失败: {0}'.format(str(e)))


class RestfulPost:
    def __init__(self, module, request_data):
        self.request = request_data
        self.module = module
        self.primary_key = inspect(module).primary_key[0].name
        self.k = [k for k in dir(module)
                  if k not in ['metadata', 'query', 'query_class', 'to_dict'] and not k.startswith("_")]

        self.filter()
        self.result = self.process()

    def filter(self):
        for k, _ in self.request.items():
            if k not in self.k:
                del self.request[k]

    def process(self):
        try:
            data = self.module(**self.request)
            db.session.add(data)
            db.session.commit()
            return getattr(self.module, 'query').get(getattr(data, self.primary_key)).to_dict()
        except Exception as e:
            app.logger.error(u'更新DB失败: {0}'.format(str(e)))
            raise SupportError(u'更新DB失败: {0}'.format(str(e)))


class RestfulDelete:
    def __init__(self, module, _id):
        self.id = _id
        self.module = module
        self.primary_key = inspect(module).primary_key[0].name
        self.result = None

        self.process()

    def process(self):
        try:
            db.session.query(self.module).filter(getattr(self.module, self.primary_key) == self.id).delete()
            db.session.commit()
            self.result = dict(status=u'删除成功!', target_id=self.id)
        except Exception as e:
            app.logger.error(u'DB删除失败: {0}'.format(str(e)))
            raise SupportError(u'DB删除失败: {0}'.format(str(e)))
