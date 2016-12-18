#-*-coding:utf-8-*-
import random
from bson import ObjectId
from flask_mail import Message
import time
from apps import config, mdb_sys
from apps.shared_tools.email.send_email import send_email
from flask import render_template
from werkzeug.security import generate_password_hash, check_password_hash

def rndChar():
    i = random.randint(1,2)
    if i == 1:
        an = random.randint(97, 122)
    else:
        an = random.randint(48, 57)
    return chr(an)

def create_email_code(user_email, cnt=6):
    _str = ""
    for t in range(cnt):
        c = rndChar()
        _str = "{}{}".format(_str,c)

    _hash_str = generate_password_hash(_str)
    _code = {'str':_hash_str, 'time':time.time()}
    mdb_sys.db.email_code.insert(_code)
    _code['_id'] = str(_code['_id'])
    # send
    if cnt == 6:
        html = render_template('online/email/code.html', code=_str)
    elif cnt == 8:
        html = render_template('online/email/ps_code.html', code=_str)
    # send email
    msg = Message("{}验证码".format(config['email'].MAIL_PROJECT),
                  sender=config['email'].MAIL_DEFAULT_SENDER,
                  recipients=[user_email])
    msg.html = html
    send_email(mdb_sys.db, msg)
    return _code

# ----------------------------------------------------------------------------------------------------------------------
def verify_email_code(code_id, code):
    r = False
    if code_id:
        _code = mdb_sys.db.email_code.find_one({'_id':ObjectId(code_id)})
        if _code:
            if check_password_hash(_code['str'], code) and time.time()-_code['time'] < config["verify"].VERIFY_FAILURE_TIME:
                r = True
    return r