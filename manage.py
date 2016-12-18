#!/usr/bin/env python
#-*-coding:utf-8-*-
from flask_script import Manager
import sys
import time
from werkzeug.security import generate_password_hash
from apps import mdb_user, create_app, mdb_cont
from apps.config import config
from apps.user.models.user import user_model

__author__ = 'all.woo'
'''
manage
'''

# create app************************************************************************************************************
#app = create_app('testing')
app = create_app('production')
manager = Manager(app)

# **********************************************************************************************************************
@manager.command
def test():

    '''Run the unit tests'''

    import unittest
    tests = unittest.TestLoader().discover('admin/tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


# **********************************************************************************************************************
@manager.command
def site_init():

    '''
        init db & create frist user & create frist role
    '''
    print('[Init] sit init')
    username = raw_input("Input username:")
    if not username:
        print("User name cannot be empty.")
        sys.exit()
    email = raw_input("Input email:")
    if not email:
        print("Email cannot be empty.")
        sys.exit()
    password = raw_input("Input password:")
    if not password:
        print("Password cannot be empty.")
        sys.exit()

    print('connected db...')
    print('create  role...')

    try:
        mdb_user.db.create_collection("role")
    except:
        pass
    try:
        mdb_user.db.create_collection("user")
    except:
        pass
    role_root = mdb_user.db.role.find_one({"permissions":config["permission"].ROOT})
    if not role_root:
        _id = mdb_user.db.role.insert({
            "name":"Root",
            "default":False,
            "permissions":config["permission"].ROOT,
            "instructions":'ROOT',

        })
    else:
        _id = role_root['_id']

    password_hash = generate_password_hash(password)
    root_user = mdb_user.db.user.find_one({"$or":[{"username":username}, {"email":email}]})
    if root_user:
        mdb_user.db.role.update({"_id":root_user._id},{"$set":{"password":password_hash}})
    else:
        print('create root user...')
        user = user_model(username=username, email=email, password=password, domain=-1, role_id=_id, active=True)
        user_id = mdb_user.db.user.insert(user)

        # profile
        user_profile = {
            'user_id':user_id,
            'user_domain':user_id,
            'avatar_url':config['user'].AVATAR_URL,
            'addr':None,
            'tel_num':None,
        }
        mdb_user.db.user_profile.insert(user_profile)

        # article type
        mdb_cont.db.article_type.insert({'user_id':user_id, 'type':[]})
        # article tag
        mdb_cont.db.article_tag.insert({'user_id':user_id, 'tag':[]})

    # ensureIndex
    print("Ensure index")
    mdb_user.db.user_profile.ensure_index([("user_id",1), ("user_domain",1)])

    print('[End] sit init')

# **********************************************************************************************************************
if __name__ == '__main__':
    manager.run()