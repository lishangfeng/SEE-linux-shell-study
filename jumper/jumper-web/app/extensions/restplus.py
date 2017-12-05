# -*- coding: utf-8 -*-

from functools import wraps
from flask import current_app as app
from flask_restplus import Api

from app import views


def load_module_dynamic(module):
    """ 动态加载模块
    """
    def _deco(f):
        @wraps(f)
        def __deco(*args, **kwargs):
            # 根据 module_chain 链式加载模块
            for name in getattr(module, 'module_priority_chain', []):
                module_name = '{0}.{1}'.format(module.__name__, name)

                try:
                    _module = __import__(module_name, fromlist=[''])
                except ImportError:
                    continue
                kwargs.update(dict(module=_module))
                f(*args, **kwargs)

            # 根据文件加载模块
            import pkgutil
            for _loader, name, _ispkg in pkgutil.iter_modules(module.__path__):
                module_name = '{0}.{1}'.format(module.__name__, name)

                # convert 'app_name.extensions.test' to 'test', then check blacklist
                if module_name.split('.')[-1] in getattr(module, 'module_blacklist', []) + getattr(module, 'module_priority_chain', []):
                    continue

                _module = __import__(module_name, fromlist=[''])

                kwargs.update(dict(module=_module))
                f(*args, **kwargs)
        return __deco
    return _deco


@load_module_dynamic(views)
def register_apis(api, **kw):
    if hasattr(kw['module'], 'restplus_api'):
        print '+' * 20, kw['module']
        api.add_namespace(kw['module'].restplus_api)
        print '  loading restplus api: %s => register' % kw['module'].__name__
    else:
        print '  loading restplus api: %s => ignore' % kw['module'].__name__


extension = Api(doc='/doc/', validate=True)
register_apis(extension)


@app.route('/_restplus/postman.json')
def postman():
    import json
    data = extension.as_postman(urlvars=False, swagger=True)
    return json.dumps(data)
