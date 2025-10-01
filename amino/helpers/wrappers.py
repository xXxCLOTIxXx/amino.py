from functools import wraps
from amino import NoCommunity, RequiredAuthorization

def require_comId(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'comId') or self.comId is None:
            raise NoCommunity("comId is required but not set in the instance.")
        return method(self, *args, **kwargs)
    return wrapper


def require_auth(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.req.sid is None:
            raise RequiredAuthorization("To perform this action you need to log in to your account.")
        return method(self, *args, **kwargs)
    return wrapper
