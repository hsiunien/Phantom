from flask import render_template, session, request, make_response, redirect, abort, url_for
from . import main
from .forms import NameForm
from ..models import User
from .. import db
from ..email import send_email


@main.route('/')
def home():
    known = session.get('known', True)
    session.pop('known', None)
    return render_template("index.html", name=session.get('name'), known=known)


@main.route('/make_request')
def req():
    cookie = request.headers.get('Cookie')
    response = make_response('<h1> current Cookie is %s<h1>' % cookie)
    response.set_cookie('sessionId', 'wxn')
    return response


@main.route('/redirect')
def rd():
    return redirect('http://www.baidu.com')


@main.route('/user/<id>')
def find_user(id):
    user = load_user(id)
    if not user:
        abort(404)
    return make_response("login success")


@main.route('/secret')
def secret():
    return 'Only authenticated users are allowed'


def load_user(id):
    return None
