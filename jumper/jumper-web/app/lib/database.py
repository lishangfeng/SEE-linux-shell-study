# -*- coding: utf-8 -*-

from sqlalchemy import inspect
from sqlalchemy.orm import relationship
from app.extensions.sqlalchemy import extension as db

# Alias common SQLAlchemy names
Column = db.Column
relationship = relationship


class FormatMixin(object):
    def to_dict(self):
        return dict([(k, getattr(self, k)) for k in self.__dict__.keys() if not k.startswith("_")])

    @classmethod
    def get_keys(cls):
        keys = [
            'metadata',
            'insert',
            'delete',
            'update',
            'get_by',
            'query_in',
            'get_by_id',
            'get_by_like',
            'query',
            'query_class',
            'to_dict',
            'get_keys',
        ]
        return [k for k in dir(cls) if not k.startswith('_') and k not in keys]


class CRUDMixin(FormatMixin):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def insert(cls, **kwargs):
        instance = cls(**kwargs)
        primary_key = getattr(instance.save(), inspect(cls).primary_key[0].name)
        db.session.close()
        return primary_key

    @classmethod
    def update(cls, query=None, data=None):
        query = query or dict()
        instance = getattr(cls, 'query').filter_by(**query)
        result = [i.to_dict() for i in instance]
        instance.update(data or dict())
        db.session.commit()
        for i in result:
            i.update(**data)
        return result

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    @classmethod
    def delete(cls, commit=True, **kwargs):
        """Remove the record from the database."""
        getattr(cls, 'query').filter_by(**kwargs).delete()
        return commit and db.session.commit()


class SurrogatePK(FormatMixin):
    """A mixin that adds a surrogate integer 'primary key' column named ``id`` to any declarative-mapped class."""

    __table_args__ = {'extend_existing': True}

    @classmethod
    def query_in(cls, key, in_list, show=''):
        result = list()
        keys = cls.get_keys()
        show = [k for k in show.split(',') if k in keys]
        if show:
            query = db.session.query(*[getattr(cls, k) for k in show])
            query = query.filter(getattr(cls, key).in_(in_list))
        else:
            query = db.session.query(cls)
            query = [i.to_dict() for i in query.filter(getattr(cls, key).in_(in_list))]
        if not show:
            result = query
        else:
            for i in query:
                data = dict()
                for k in keys:
                    if hasattr(i, k):
                        data[k] = getattr(i, k)
                else:
                    result.append(data)
        return result

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        data = getattr(cls, 'query').get(record_id)
        if data:
            return data.to_dict()
        return dict()

    @classmethod
    def get_by(cls, first=False, show='', **kwargs):
        result = list()
        keys = cls.get_keys()
        show = [k for k in show.split(',') if k in keys]
        if show:
            query = db.session.query(*[getattr(cls, k) for k in show])
            for k, v in kwargs.items():
                query = query.filter(getattr(cls, k) == v)
        else:
            query = [i.to_dict() for i in getattr(cls, 'query').filter_by(**kwargs)]

        if not show:
            result = query
        else:
            for i in query:
                data = dict()
                for k in keys:
                    if hasattr(i, k):
                        data[k] = getattr(i, k)
                else:
                    result.append(data)
        if first:
            return result[0] if result else list()
        else:
            return result

    @classmethod
    def get_by_like(cls, **kwargs):
        query = db.session.query(cls)
        for k, v in kwargs.items():
            query = query.filter(getattr(cls, k).like('%{0}%'.format(v)))
        return [i.to_dict() for i in query]


class Model(db.Model, SurrogatePK, CRUDMixin, FormatMixin):
    """Base model class that includes CRUD convenience methods."""
    __abstract__ = True


def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.
    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return db.Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)
