#!/usr/bin/env python
#-*-coding:utf-8-*-
import logging
import sys
import os
from apps.db_config import config as db_config

__author__ = 'woo'

basedir=os.path.abspath(os.path.dirname(__file__))

class Config:

    @staticmethod
    def init_app(app):
        pass

# **********************************************************************************************************************
class TestingConfig(Config):

    _debug = True

#***********************************************************************************************************************
class ProductionConfig(Config):

    _debug = False


SITE_NAME = u"OSNOOB｜菜鸟源"

class Title(Config):

    TITLE = "OSNOOB|菜鸟源"
    HOME_TITLE_PC = 'OSNOOB | 菜鸟源地, 开源CMS'
    HOME_TITLE_M = 'OSNOOB开源'


# email server**********************************************************************************************************
class Email(Config):
    '''
    email server
    '''
    # Flask-Mail configuration
    MAIL_SERVER = 'smtp.mxhichina.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_ASCII_ATTACHMENTS = True
    MAIL_DEFAULT_SENDER = 'system@noobw.com'
    MAIL_USERNAME = "system@noobw.com"
    MAIL_PASSWORD = db_config['key'].EMAIL_PW
    #
    MAIL_PROJECT = "OSNOOB"

    # administrator list
    ADMINS = ['system@noobw.com']


    LOSE_VER_HTML = '<p>您的验证链接已过期,或者无效,请检查.<a style="color:#1AB667;" href="{}">重新发送</a></p>'

    VER_HTML = '<p>用户{}注册邮箱未验证！</p><p>没收到邮件或者邮件失效了？<a href="{}" style="color:#1AB667;">重新发送</a></p>'

    REGISTER_VER_HTML = '<p>欢迎来到%s！验证邮件已发送到了{}邮箱，请查收并验证!</p>'' \
                        ''<p>若没收到邮件(确认是否被视为垃圾邮件)或者邮件失效了,点击　' \
                        '<a style="color:#1AB667;" href="{}" 　>重新发送</a>' \
                        '</p>'%(SITE_NAME)

# **********************************************************************************************************************
class Cache(Config):

    '''
    Secret
    '''

    CACHE_TYPE = 'sample'


# **********************************************************************************************************************
class Session(Config):
    '''
    session
    '''
    SESSION_TYPE = 'filesystem'


# **********************************************************************************************************************
class Paging(Config):
    '''
    paging
    '''
    FLASKY_USERS_PER_PAGE = 15
    FLASKY_ROLES_PER_PAGE = 10
    POST_PER_PAGE = 10
    POST_PER_PAGE_HOME = 10
    POST_PER_PAGE_RE = 5
    POST_SEARCH = 10
    POST_COMMENT = 10
    # front


# **********************************************************************************************************************
class Upload(Config):

    '''
    图片上传配置
    '''

    IMG_HOST = db_config['upload'].IMG_HOST
    AVA_HOST = db_config['upload'].AVA_HOST
    IMG_B = db_config['upload'].IMG_B
    AVA_B = db_config['upload'].AVA_B

    # ---------------------------------------
    POST_THU = "?imageView/2/w/360/h/230"
    AVA_THU = "?imageView/2/w/250/h/250"
    POST_BODY_THU = "?imageView/2/w/740"

    # ----------------------------------------
    HOST = '{}/apps/static'.format(sys.path[0])
    # These are the extension that we are accepting to be uploaded
    ALLOWED_EXTENSIONS= set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'ico'])
    IMG_PROJECT = [('adv', u'推广'), ('show', u'展示'), ('post', u'Post'), ('sys_default','网站图标')]

# **********************************************************************************************************************
class User(Config):
    
    '''
    Site default path
    '''
    
    AVATAR_URL = [{
                "bucket" : "user-avatars",
                "d" : "avatar",
                "key" : "avatar-default.png"
            },
        {
                "bucket" : "user-avatars",
                "d" : "avatar",
                "key" : "avatar-default1.png"
            },
        {
                "bucket" : "user-avatars",
                "d" : "avatar",
                "key" : "avatar-default2.png"
            },
        {
                "bucket" : "user-avatars",
                "d" : "avatar",
                "key" : "avatar-default3.png"
            },
        {
                "bucket" : "user-avatars",
                "d" : "avatar",
                "key" : "avatar-default4.png"
            },
        {
                "bucket" : "user-avatars",
                "d" : "avatar",
                "key" : "avatar-default5.png"
            },
        {
                "bucket" : "user-avatars",
                "d" : "avatar",
                "key" : "avatar-default6.png"
            },
        {
                "bucket" : "user-avatars",
                "d" : "avatar",
                "key" : "avatar-default7.png"
            },
        {
                "bucket" : "user-avatars",
                "d" : "avatar",
                "key" : "avatar-default8.png"
            },
        {
                "bucket" : "user-avatars",
                "d" : "avatar",
                "key" : "avatar-default9.png"
            }
        ]


# **********************************************************************************************************************
class Cache(Config):

    CACHE_TYPE = 'filesystem'
    CACHE_DEFAULT_TIMEOUT = 60
    CACHE_DIR = '{}/web_cache_dir'.format(basedir)
    CACHE_THRESHOLD = 1000

class CacheTimeout(Config):

    POSTS = 60
    POST = 0.5
    USER_POSTS = 1
    POST_TYPE = 0.5

# **********************************************************************************************************************
class Comment(Config):

    PASS_CNT = 3
    COMMENT_MAX = 300
    INTERVAL = 20

class Post(Config):

    DOMAIN = "http://www.osnoob.com"
    IMG_PATH = 'images/post_img'
    SUBJECT = ['tech', 'wide', 'sys', 'art']
    NEW_PV = 30


# --------------------------------------------------------------------------------------------
class WebLogger():
    NORMAL = logging.INFO
    EXCEP = logging.ERROR

# --------------------------------------------------------------------------------------------
class Cookie():
    POST_TIMEOUT = 3600*60

class OAuthLogin():

    EMAIL_LIST = ['app_3_qq_login@noobw.com']
# --------------------------------------------------------------------------------------------
class Version():
    VERSION = 160709

class Permission():

    '''
    Rights management role
    '''

    AVERABGEUSER = 0b00000001
    ECP =          0b00001000
    EDITOR =       0b00010000
    AUDITOR =      0b00100000
    ADMINISTER =   0b01000000
    ROOT =         0b10000000

# **********************************************************************************************************************
config = {
    'testing':TestingConfig,
    'production':ProductionConfig,
    'session':Session,
    'paging':Paging,
    'email':Email,
    'upload':Upload,
    'user':User,
    'cache':Cache,
    'cache_timeout':CacheTimeout,
    'comment':Comment,
    'post':Post,
    'weblogger':WebLogger,
    'title':Title,
    'cookie':Cookie,
    'oauth_login':OAuthLogin,
    'version':Version,
    'permission':Permission,
}





