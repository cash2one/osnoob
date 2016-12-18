import time
from werkzeug.security import generate_password_hash

__author__ = 'woo'


def user_model(**kwargs):
    if not kwargs["username"]:
        return None
    if not kwargs["domain"]:
        return None
    if not kwargs["password"]:
        return None
    if not kwargs["email"]:
        return None
    if not kwargs["role_id"]:
        return None

    if "active" in kwargs:
        active = kwargs["active"]
    else:
        active = False
    user = {
        "username":kwargs["username"],
        "domain" :kwargs["domain"],
        "password" :generate_password_hash(kwargs["password"]),
        "email" :kwargs["email"],
        "create_at":time.time(),
        "update_at":time.time(),
        "active":active,
        "is_delete" :False,
        "role_id":kwargs["role_id"],
    }

    return user
