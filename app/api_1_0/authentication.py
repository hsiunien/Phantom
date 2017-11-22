from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth

from app.api_1_0.errors import forbidden
from app.models import AnonymousUser, User
from . import api

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password, **kwargs):
    if not email_or_token:
        g.current_user = AnonymousUser()
        return True
    if not password:
        uuid = kwargs.get("uuid")
        g.current_user = User.verify_auth_token(email_or_token, uuid)
        g.token_used = True
        return g.current_user is not None

    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return forbidden('Invalid credentials')


@api.before_request
@auth.login_required
def befor_request():
    if (not g.current_user.is_anonymous) and not g.current_user.confirmed:
        return forbidden("un confirmed account")


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return forbidden('Invalid credentials when you get token')
    return jsonify(token=g.current_user.generate_auth_token(), expiration=3600 * 24)


@api.route('/user/<int:id>')
def get_user(id):
    u = User.query.get_or_404(id)
    return jsonify(u.to_json())
