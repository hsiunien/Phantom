from flask import render_template, session, request, make_response, redirect, abort, url_for
from flask_login import login_required

from app.decorator import admin_required, permission_required
from app.models import Permission
from . import main


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


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For admin only"


@main.route('/moderate')
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators():
    return "FOr moderator"


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
