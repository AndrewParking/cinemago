from functools import wraps
from flask import request, g
from .exceptions import Unauthorized, Forbidden
from .admin.models import User


def auth_required(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        token = request.headers.get('Auth-Cinemago-Token')
        if token is None:
            raise Unauthorized('You need to provide auth header for this resource.')
        g.current_user = User.verify_auth_token(token)
        return f(self, *args, **kwargs)
    return wrapper


def permission_required(*permissions):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            user = g.current_user
            if user is None:
                raise Forbidden('Anon users are not allowed.')
            # -----------------------------------------------------
            if len(permissions) == 1:
                perms = permissions[0].value
            else:
                perms = 0x0
                for p in permissions:
                    perms = perms | p.value
            # -----------------------------------------------------
            if (user.role.permissions & perms) != perms:
                raise Forbidden('You don\'t have required permissions.')
            return f(self, *args, **kwargs)
        return wrapper
    return decorator
