import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from app.models import User, Role, Post

COV = None
if os.environ.get("COVERAGE"):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

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
def test(coverage=False):
    if coverage and not os.environ.get('COVERAGE'):
        import sys
        os.environ['COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print("Coverage summary:")
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print("HTML version:file://%s/index.html" % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler """
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run the deployment tasks"""
    from  flask_migrate import upgrade
    from app.models import Role, User
    upgrade()

    Role.insert_roles()
    User.follow_them_self()


if __name__ == '__main__':
    manager.run()
