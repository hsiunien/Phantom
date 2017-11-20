from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from app.models import User, Role, Post

app = create_app('default')
DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']
# in order to resolve the issue:alembic no support for alter of constraints in sqlite dialect
is_sqlite = DATABASE_URI.startswith('sqlite:')
manager = Manager(app)
migrate = Migrate()
migrate.init_app(app, db, render_as_batch=is_sqlite)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
