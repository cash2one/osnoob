# -*-coding:utf-8-*-
import os
import re
from flask import Flask, render_template, g, request
from flask_cache import Cache
from flask_mail import Mail
from flask_moment import Moment
from flask_oauthlib.client import OAuth
from flask_pymongo import PyMongo
from flask_session import Session
from flask_wtf import CsrfProtect
from werkzeug.utils import redirect
from apps.config import config, SITE_NAME
from apps.db_config import config as db_config
from flask_bootstrap import Bootstrap
from qiniu import Auth
from flask_login import LoginManager, current_user
from apps.weblogger.access import logger
from apps.shared_tools.request.my_request import MyRequest

'''
 __author__ = 'woo'
 Module to initialize and config flask application.
'''

# Flask Create extension instances**************************************************************************************
#app = Flask(__name__, static_folder='themes', static_url_path='/themes/{}'.format(config["theme"].THEME_NAME))
app = Flask(__name__, static_folder='themes', static_url_path='/themes')
mdb_user = PyMongo()
mdb_sys = PyMongo()
mdb_cont = PyMongo()
cache = Cache()
csrf = CsrfProtect()
bootstrap = Bootstrap()
login_manger = LoginManager()
moment = Moment()
sess = Session()
mail = Mail()
qn = Auth(db_config['qiniu'].ACCESS_KEY, db_config['qiniu'].SECRET_KEY)

login_manger.session_protection = 'strong'
login_manger.login_view = 'online.login'
log = logger()
oauth = OAuth()

# app config---------------------------------------------------------------------
app.config.from_object(db_config['database'])
app.config.from_object(config['email'])
app.config.from_object(config['paging'])
app.config.from_object(config['cache'])
app.config.from_object(config['session'])
app.config.from_object(db_config['csrf'])
app.config.from_object(db_config['key'])
app.config.from_object(config['upload'])

# init---------------------------------------------------------------------------
mdb_user.init_app(app, config_prefix='MONGO_USER')
mdb_cont.init_app(app, config_prefix='MONGO_CONT')
mdb_sys.init_app(app, config_prefix='MONGO_SYS')
cache.init_app(app)
sess.init_app(app)
csrf.init_app(app)
bootstrap.init_app(app)
login_manger.init_app(app)
moment.init_app(app)
mail.init_app(app)
log.init_app(app)
oauth.init_app(app)

# oauth --------------------------------------------------------------------------
#QQ
QQ_APP_ID = os.getenv('QQ_APP_ID', db_config['my_oauth'].QQ_APP_ID)
QQ_APP_KEY = os.getenv('QQ_APP_KEY', db_config['my_oauth'].QQ_APP_KEY)
qq = oauth.remote_app(
    'qq',
    consumer_key=QQ_APP_ID,
    consumer_secret=QQ_APP_KEY,
    base_url='https://graph.qq.com',
    request_token_url=None,
    request_token_params={'scope': 'get_user_info'},
    access_token_url='/oauth2.0/token',
    authorize_url='/oauth2.0/authorize',
)

# register blueprint----------------------------------------------------------
from apps.blueprint import api, base, admin, online, people, comments, post, media, audit, pay
# admin
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(media, url_prefix="/media")
app.register_blueprint(pay, url_prefix="/pay")

# user
app.register_blueprint(base)
app.register_blueprint(online, url_prefix="/account")
app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(people, url_prefix="/people")
app.register_blueprint(comments, url_prefix="/comment")
app.register_blueprint(post, url_prefix="/post")
app.register_blueprint(audit, url_prefix="/audit")


# -----------------------------------------------------------------------------
def create_app(environment):
    app.debug = config[environment]._debug
    return app


# 404 400 500-----------------------------------------------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('{}/exception/404.html'.format(config["theme"].THEME_NAME), view_data={'title':u'该页面不存在了-{}'.format(SITE_NAME)}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('{}/exception/400.html'.format(config["theme"].THEME_NAME), request_id=g.request_id, view_data={'title':u'该页面不存在了-{}'.format(SITE_NAME)}), 500

@app.errorhandler(400)
def internal_server_error(e):
    return render_template('{}/exception/400.html'.format(config["theme"].THEME_NAME), request_id=g.request_id, view_data={'title':u'该页面不存在了-{}'.format(SITE_NAME)}), 400


# API --------------------------------------------------------------------------------------
@app.before_request
def api_csrf():
    g.version = config['version'].VERSION
    if "/api/" in request.url:
        csrf.protect()

    elif "m.noobw.com" in request.url:
        #g.tn = "m"
        userAgent = request.headers['User-Agent']
        _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
        _long_matches = re.compile(_long_matches, re.IGNORECASE)
        _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
        _short_matches = re.compile(_short_matches, re.IGNORECASE)
        user_agent = userAgent[0:4]
        if _long_matches.search(userAgent) != None:
            m_url = request.url.replace("http://www.","http://m.")

            g.tn = "m"

        elif _short_matches.search(user_agent) != None:
            g.tn = "m"
        else:
            m_url = request.url.replace("http://m.","http://www.")
            if "http://www." in m_url:
                return redirect(m_url)

    else:
        userAgent = request.headers['User-Agent']
        _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
        _long_matches = re.compile(_long_matches, re.IGNORECASE)
        _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
        _short_matches = re.compile(_short_matches, re.IGNORECASE)
        user_agent = userAgent[0:4]
        if _long_matches.search(userAgent) != None:
            m_url = request.url.replace("http://www.","http://m.")
            if "http://m." in m_url:
                return redirect(m_url)
            else:
                g.tn = "m"

        elif _short_matches.search(user_agent) != None:
            m_url = request.url.replace("http://www.","http://m.")
            if "http://m." in m_url:
                return redirect(m_url)
            else:
                g.tn = "m"
        else:
            g.tn = "pc"


# # Global news************************************************************************
@app.before_request
def msg():
    request.value = MyRequest()
    g.imghost = config['upload'].IMG_HOST
    g.avahost = config['upload'].AVA_HOST
    g.post_thu = config['upload'].POST_THU
    g.ava_thu = config['upload'].AVA_THU
    g.theme_name = config["theme"].THEME_NAME
    if current_user.is_authenticated:
        g.msg = {}
        g.msg['msgs'] = mdb_user.db.msg.find({'user_id':current_user.id, 'case_status':1, 'status':0})
        g.msg['cnt'] = g.msg['msgs'].count()
        user_profile = mdb_user.db.user_profile.find_one({'user_id':current_user.id})
        if user_profile:
            g.user_avatar_url = user_profile['avatar_url']
        # company



