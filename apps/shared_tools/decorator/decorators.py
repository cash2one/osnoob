#-*-coding:utf-8-*-
from threading import Thread
from flask_login import current_user
from functools import wraps
from flask import abort
__author__ = 'woo'
'''
decorators
'''

# permission required**************************************************************************************************
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(404)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# 异步多线程调用**********************************************************************************************************
def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
    return wrapper




