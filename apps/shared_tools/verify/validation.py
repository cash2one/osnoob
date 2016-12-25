
from flask_login import current_user
from werkzeug.exceptions import abort
from apps import mdb_user
from apps.config import Permission

__author__ = 'woo'


def is_myself(domain):
    if current_user.is_anonymous():
        return False
    up = mdb_user.db.user_profile.find_one({'user_domain':domain})
    if up:
        if up['user_id'] == current_user.id:
            return True
        else:
            return False
    else:
        abort(404)

# ----------------------------------------------------------------------------------------------------------------------
def is_self_admin(user_id):

    if current_user.is_anonymous():
        abort(404)
    elif user_id != current_user.id and not current_user.can(Permission.AUDITOR):
        abort(404)
