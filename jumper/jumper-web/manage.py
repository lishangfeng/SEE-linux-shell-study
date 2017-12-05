# -*- coding: utf-8 -*-

from flask_script import Shell
from flask_script import Server
from flask_script import Option
from flask_script import Command
from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand
from flask_script.commands import Clean
from flask_script.commands import ShowUrls

from app.main import app
from tools.flush import Config
from tools.flush import FlushNSS
from tools.flush import FlushSudo
from tools.flush import FlushHost
from tools.tmp_account import TMPAccount
from tools.upload_repair import Upload
from tools.flush import UpgradeCache
from app.lib.database import db
from jobs.sync_redis import SyncCache
from jobs.sync_mysql import SyncMysql
from jobs.sync_userinfo import SyncUserInfo
from jobs.clean_expired import CleanExpired


manager = Manager(app)

is_sqlite = app.config.get('SQLALCHEMY_DATABASE_URI').startswith('sqlite:')
migrate = Migrate(app, db, render_as_batch=is_sqlite, compare_type=True)


def _make_context():
    return dict(app=app, db=db)


class GunicornServer(Command):
    """Run the app within Gunicorn"""

    def get_options(self):
        from gunicorn.config import make_settings

        settings = make_settings()
        options = (
            Option(
                    *klass.cli,
                    action=klass.action,
                    **({'const': klass.const} if klass.const is not None else {})
            ) for setting, klass in settings.iteritems() if klass.cli
        )
        return options

    def run(self, *args, **kwargs):
        from gunicorn.app.wsgiapp import WSGIApplication
        _app = WSGIApplication()
        _app.app_uri = 'manage:app'
        return _app.run()


manager.add_command("tmp", TMPAccount())
manager.add_command("upload", Upload())
manager.add_command("clean-expired", CleanExpired())
manager.add_command("sync-cache", SyncCache())
manager.add_command("sync-mysql", SyncMysql())
manager.add_command("sync-userinfo", SyncUserInfo())
manager.add_command("upgrade_cache", UpgradeCache())
manager.add_command("flush-nss", FlushNSS())
manager.add_command("flush-sudo", FlushSudo())
manager.add_command("flush-host", FlushHost())
manager.add_command('clean', Clean())
manager.add_command('config', Config())
manager.add_command('url', ShowUrls())
manager.add_command('db', MigrateCommand)
manager.add_command("gunicorn", GunicornServer())
manager.add_command("shell", Shell(make_context=_make_context))
manager.add_command('server', Server(host=app.config.get('HOST', '0.0.0.0'), port=app.config.get('PORT', 8080)))
manager.add_command('dev', Server(host=app.config.get('HOST', '0.0.0.0'), port=app.config.get('PORT', 8080), use_debugger=True))

if __name__ == '__main__':
    manager.run()
