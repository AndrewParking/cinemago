import os
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from app import create_app, db
from app.admin.models import Role, User
from commands import TestCommand


app = create_app(os.environ.get('CINEMAGO_CONF_MODE') or 'development')

manager = Manager(app)
migrate = Migrate(app, db)

def make_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command('shell', Shell(banner=app.config['SHELL_BANNER'], make_context=make_context))
manager.add_command('db', MigrateCommand)
manager.add_command('test', TestCommand)


if __name__ == '__main__':
    manager.run()
