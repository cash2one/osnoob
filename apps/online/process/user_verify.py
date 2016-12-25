from bson import ObjectId
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from apps import login_manger, mdb_user
from apps.config import Permission

__author__ = 'woo'


class User(UserMixin):

    '''
    @author allen.woo'
    '''


    def __init__(self, _user=None, _id=None, **kwargs):
        super(User, self).__init__(**kwargs)

        if _id and not _user:
            user = mdb_user.db.user.find_one({"id":_id})
        elif _user:
            self.user = _user
            self.password_hash = self.user["password"]
            self.id = self.user["_id"]
            self.username = self.user["username"]
            self.email = self.user["email"]
            self.is_delete = self.user["is_delete"]
            self.active = self.user["active"]
        else:
            return None

    @property
    def password(self):
        raise ArithmeticError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def generate_password_hash(self, password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def auth_judge(self, permissions):
        role = mdb_user.db.role.find_one({"_id":ObjectId(self.user["role_id"])})

        return role and permissions <= role['permissions'] and self.user["active"] and not self.user["is_delete"]

    def can(self, permissions):
        role = mdb_user.db.role.find_one({"_id":ObjectId(self.user["role_id"])})
        return role and permissions <= role["permissions"] and self.user["active"] and not self.user["is_delete"]

    def is_role(self, permissions):
        role = mdb_user.db.role.find_one({"_id":ObjectId(self.user["role_id"])})
        return role and permissions == role["permissions"] and self.user["active"] and not self.user["is_delete"]

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_root(self):
        return self.can(Permission.ROOT)


    def is_active(self):
        return self.user["active"]

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return self.username


def password_hash(password):
    return generate_password_hash(password)


# Load the user callback function***************************************************************************************
@login_manger.user_loader
def load_user(user_id):
    user = mdb_user.db.user.find_one({"_id":ObjectId(user_id)})
    if user:
        return User(user)
    else:
        return None

