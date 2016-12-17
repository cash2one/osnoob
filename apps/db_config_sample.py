#!/usr/bin/env python
#-*-coding:utf-8-*-
from logging import FileHandler
import os
__author__ = 'woo'

basedir=os.path.abspath(os.path.dirname(__file__))


class Config:

    @staticmethod
    def init_app(app):
        pass


# **********************************************************************************************************************
class Database(Config):
    '''
    database
    '''

    # SQL
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/noobw'
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir,'db_repository')

    #MONGODB--zwsj
    MONGO_AUTO_START_REQUEST = False
    MONGO_DBNAME = 'noobw'
    MONGO_HOST = '127.0.0.1'
    MONGO_PORT = 27017
    MONGO_USERNAME = 'wooadm'
    MONGO_PASSWORD = '123456'
    #
    #MONGODB--sys
    MONGO_SYS_AUTO_START_REQUEST = False
    MONGO_SYS_DBNAME = 'nw_sys'
    MONGO_SYS_HOST = '127.0.0.1'
    MONGO_SYS_PORT = 27017
    MONGO_SYS_USERNAME = 'wooadm'
    MONGO_SYS_PASSWORD = '123456'


# **********************************************************************************************************************
class Key(Config):
    SECRET_KEY = "53vdve$%^#$gsdgsr"
    SECURITY_PASSWORD_SALT = "afgerwa5%vdfvdffdbvgsdfi"
    EMAIL_PW = "#N0fsdfd3..?!"

# **********************************************************************************************************************
class Csrf(Config):

    '''
    CSRF
    '''
    CSRF_ENABLED = True

# *********************************************************************************************************************
class Qiniu():

    ACCESS_KEY = "yigdf34534gdsfg-5qgdfgU5"
    SECRET_KEY= "qgfsghsrthdytjdfgtj"
# **********************************************************************************************************************
config = {
    'database':Database,
    'key':Key,
    'csrf':Csrf,
    'qiniu':Qiniu,
}

