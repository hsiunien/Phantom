from flask import Flask, request, redirect, abort, render_template
from flask import make_response, session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
import os
from flask_script import Shell
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread

base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = '5551133'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


###email

app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'zens53@163.com'
app.config['MAIL_PASSWORD'] = 'i1ovey1'

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[FLASKY]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky admin<zens53@163.com>'
mail = Mail(app)

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)






