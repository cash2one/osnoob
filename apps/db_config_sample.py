#!/usr/bin/env python
#-*-coding:utf-8-*-
from logging import FileHandler
import os
from pymongo import ReadPreference

__author__ = 'woo'

basedir=os.path.abspath(os.path.dirname(__file__))


class Config:

    @staticmethod
    def init_app(app):
        pass

class Database(Config):


    '''
    database
    '''

    #MONGODB
    hosts_uri = "mongodb://userweb:123456@127.0.0.1:27017/{}"
    MONGO_USER_URI = { "mongodb":hosts_uri.format("osn_user"),
            "db":"osn_user",
            'replica_set': None,
            "fsync":False,
            "read_preference":ReadPreference.SECONDARY_PREFERRED,
            }

    MONGO_CONT_URI = { "mongodb":hosts_uri.format("osn_content"),
            "db":"osn_content",
            "fsync":False,
            'replica_set': None,
            "read_preference":ReadPreference.SECONDARY_PREFERRED,
            }

    MONGO_SYS_URI = { "mongodb":hosts_uri.format("osn_sys"),
            "db":"osn_sys",
            "fsync":False,
            'replica_set': None,
            "read_preference":ReadPreference.SECONDARY_PREFERRED,
            }

    # # Redis----------------------------------------------------------------
    # REDIS_HOST = '192.168.1.120'
    # REDIS_PORT = '6379'
    # REDIS_PASSWORD = None


# **********************************************************************************************************************
class Key(Config):
    SECRET_KEY = "534!@$#f#&*fvdevfd@)$#*$#r"
    SECURITY_PASSWORD_SALT = "afgerwa5%^$%^vaf@#(&^vfreg"
    EMAIL_PW = "#N00bw#5323..?!"

# **********************************************************************************************************************
class Csrf(Config):

    '''
    CSRF
    '''
    CSRF_ENABLED = False
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_METHODS = []#['GET','POST', 'PUT', 'PATCH','DELETE']
    SECRET_KEY = "bvdfvvsdvsdtdbnsjhnmdfjmndghkjdjkd"

# *********************************************************************************************************************
class Qiniu():

    ACCESS_KEY = "yizLx8RpVKvOi7UqJpH4d4wnlUSwHNojG-5qOXU5"
    SECRET_KEY= "qvzGv02GS2LGEQwLmx0PYPryPJBfBkSkhe9Ph5dg"

class Upload(Config):

    IMG_HOST = "test-img.noobw.com"
    AVA_HOST = "test-avatar.noobw.com"
    IMG_B = "test-image"
    AVA_B = "test-avatar"

class MyOauth(Config):

    QQ_APP_ID = '101325657'
    QQ_APP_KEY = 'a8e9682e10c5d4144fd12735777b7ef8'

# **********************************************************************************************************************
config = {
    'database':Database,
    'key':Key,
    'csrf':Csrf,
    'qiniu':Qiniu,
    'upload':Upload,
    'my_oauth':MyOauth,
}
