from functools import wraps

from flask import g

from app.api_1_0.errors import forbidden


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorate_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden("您无此操作权限")
            return f(*args, **kwargs)

        return decorate_function

    return decorator
