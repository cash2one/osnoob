# -*-coding:utf-8-*-
import json
from random import randint
from flask import session, url_for, request
from flask_login import login_user
import time
from werkzeug.utils import redirect
from apps import db_config, qq, db, mdb, config
from apps.admin.models.user import User, Role, Permission
from apps.blueprint import online
from apps.shared_tool.image_up import  img_fetch
from apps.verify.process.ver_code import rndChar

__author__ = 'woo'

def json_to_dict(x):

    '''OAuthResponse class can't not parse the JSON data with content-type
    text/html, so we need reload the JSON data manually'''

    if x.find('callback') > -1:
        pos_lb = x.find('{')
        pos_rb = x.find('}')
        x = x[pos_lb:pos_rb + 1]
    try:
        return json.loads(x, encoding='utf-8')
    except:
        return x


def update_qq_api_request_data(data={}):

    '''Update some required parameters for OAuth2.0 API calls'''

    defaults = {
        'openid': session.get('qq_openid'),
        'access_token': session.get('qq_token')[0],
        'oauth_consumer_key': db_config['my_oauth'].QQ_APP_ID,
    }
    defaults.update(data)
    return defaults

def oauth_login_register(open_id,oauth_app,username, sex,email, ava_url=None, province="",city="",district=""):
    #　验证是否第一次
    if oauth_app == "qq":
        up = mdb.db.user_profile.find_one({'qq_openid':open_id})
        if up:
            user = User.query.filter_by(username=up['username']).first()
            login_user(user, False)
            return 0


    # 第一次登录---------------------------------------------------------------------------
    t_uaername = username
    while User.query.filter_by(username=username).first():
        username = "{}_{}".format(t_uaername, randint(1000,100000))

    role_id = Role.query.filter_by(permissions=Permission.AVERABGEUSER).first().id
    password = ""
    for i in range(0,10):
        password = "{}{}".format(password, rndChar())
    user = User(username=username,
                        email=email,
                        password=password,
                        role_id=role_id,
                        active = 1,
                        )
    db.session.add(user)
    db.session.commit()

    # profile

    if not ava_url:
        avatar_l = len(config['user'].AVATAR_URL)
        avatar_url = config['user'].AVATAR_URL[randint(0,avatar_l-1)]
    else:
        bucket_name = {'b':config['upload'].AVA_B, 'domain':'avatar', 'project':'avatar'}
        r = img_fetch(ava_url, bucket_name)
        avatar_url = r['url']
    if r['url'] == -1:
        avatar_l = len(config['user'].AVATAR_URL)
        avatar_url = config['user'].AVATAR_URL[randint(0,avatar_l-1)]

    user_profile = {
        'crate_time':time.time(),
        'user_id':user.id,
        'user_domain':user.id,
        'username':user.username,
        'sex':sex,
        'info':'',
        'email':user.email,
        'avatar_url':avatar_url,
        'addr':{'country':None,'provinces':province, 'city':city,'district':district},
        'tel_num':None,
        "pay":{'alipay':{'use':0}, 'webchatpay':{'use':0}},
        "oauth-app":oauth_app,
    }
    if oauth_app == "qq":
        user_profile['qq_openid'] = open_id
    mdb.db.user_profile.insert(user_profile)
    # post type
    mdb.db.post_type.insert({'user_id':user.id, 'type':[]})
    # post tag
    mdb.db.tag.insert({'user_id':user.id, 'tag':[]})
    login_user(user, False)
    return 0

@online.route('/user_info')
def get_user_info():
    if 'qq_token' in session:
        data = update_qq_api_request_data()
        resp = qq.get('/user/get_user_info', data=data)
        _data = json.loads(resp.data, encoding='utf-8')
        if resp.status==200 and not _data['ret']:
            username = _data['nickname']
            if _data['gender'] == "男" or _data['gender'] == u"男":
                sex = 0
            else:
                sex = 1
            #
            if "figureurl_qq_2" in _data and _data["figureurl_qq_2"]:
                ava_url = _data["figureurl_qq_2"]
            elif "figureurl_2" in _data and _data["figureurl_2"]:
                ava_url = _data["figureurl_2"]
            else:
                ava_url = None
            #
            if "qq_openid" in session:
                qq_openid = session['qq_openid']
            oauth_login_register(oauth_app="qq",
                                 open_id = qq_openid,
                                 username=username,
                                 sex = sex,
                                 email="app_3_qq_login@noobw.com",
                                 ava_url=ava_url,
                                 province=_data['province'],
                                 city=_data['city'],

                                 )
        return redirect(url_for('online.index'))
    return redirect(url_for('online.login_oauth'))


@online.route('/sign-in/oauth')
def login_oauth():
    return qq.authorize(callback=url_for('online.authorized', _external=True))

@online.route('/login/authorized')
def authorized():
    resp = qq.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['qq_token'] = (resp['access_token'], '')

    # Get openid via access_token, openid and access_token are needed for API calls
    resp = qq.get('/oauth2.0/me', {'access_token': session['qq_token'][0]})
    resp = json_to_dict(resp.data)
    if isinstance(resp, dict):
        session['qq_openid'] = resp.get('openid')

    return redirect(url_for('online.get_user_info'))

@qq.tokengetter
def get_qq_oauth_token():
    return session.get('qq_token')

