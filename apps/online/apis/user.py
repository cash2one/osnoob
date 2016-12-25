#!/usr/bin/env python
#-*-coding:utf-8-*-
from random import randint
from flask import request, jsonify, flash, url_for, render_template
import time
from flask_login import login_required, current_user
from flask_mail import Message
from apps.blueprint import api
from apps.config import Permission
from apps import mdb_user, mdb_sys, config, mdb_cont
from apps.online.process.user import password_format, p_email_change, p_password_reset, login_sha, p_retrieve_password
from apps.online.process.user_verify import User
from apps.shared_tools.email.email_format import ver_email
from apps.shared_tools.email.send_email import send_email
from apps.shared_tools.email.token import generate_confirmation_token
from apps.shared_tools.region.addr_format import addr_f
from apps.user.models.user import user_model
from apps.verify.process.email_format import is_email
from apps.verify.process.ver_code import verify_code, vercode_del, create_code

__author__ = 'woo'

# --------------------------------------------------------------------------------------------------------
@api.route('/sign-up', methods=['POST'])
def sign_up():

    _data = {'flash':None}
    role = mdb_user.db.role.find_one({"permissions":Permission.AVERABGEUSER})
    if role:
        role_id = role['_id']
    # code
    email = request.value.all['email'].strip()
    username = request.value.all['username'].strip()
    password = request.value.all['password'].strip()
    password2 = request.value.all['password2'].strip()
    code = request.value.all['vercode'].strip()
    code_url = request.value.all['code_url']
    r = verify_code(code_url, code)
    if not ver_email(email):
        _data['flash'] = {'msg':'邮箱格式错误！', 'type':'e'}
    elif not r:
        _data['flash'] = {'msg':'验证码错误！', 'type':'e'}
        vercode_del(code_url)
    elif password2 != password:
        _data['flash'] = {'msg':'两次密码不一致！', 'type':'e'}
    elif mdb_user.db.user.find_one({"email":email}):
        _data['flash'] = {'type':'w','msg':u'此邮箱已在该网站注册过哦，请直接登录！'}

    elif mdb_user.db.user.find_one({"username":username}):
        _data['flash'] = {'type':'w','msg':u'此名号已被使用，请再取一个吧！'}

    if not _data['flash']:
        names = mdb_sys.db.audit_rules.find_one({'type':'username'})
        try:
            t_username = username.upper()
        except:
            t_username = username
        if t_username in names['rule']:
            _data['flash'] = {'type':'w','msg':u'此名号已被使用，请再取一个吧！'}

    # password--------------------------------------------------------------------------------------------------
    if not _data['flash']:
        r = password_format(password)
        if 'flash' in r:
            _data['flash'] = r['flash']

    if not _data['flash']:
        if is_email(email):
            user = user_model(username=username, email=email, password=password, domain=-1, role_id=role_id)
            user_id = mdb_user.db.user.insert(user)
            user = User(mdb_user.db.user.find_one({"_id":user_id}))
            # 邮箱验证加密链接
            token = generate_confirmation_token(user.email)

            # profile
            avatar_l = len(config['user'].AVATAR_URL)
            avatar_url = config['user'].AVATAR_URL[randint(0,avatar_l-1)]
            user_profile = {
                'crate_time':time.time(),
                'user_id':user.id,
                'user_domain':user.id,
                'username':user.username,
                'info':'',
                'email':user.email,
                'avatar_url':avatar_url,
                'addr':{'country':None,'provinces':None, 'city':None,'district':None},
                'tel_num':None,
                "pay":{'alipay':{'use':0}, 'webchatpay':{'use':0}}

            }
            mdb_user.db.user_profile.insert(user_profile)
            # article type
            mdb_cont.db.article_type.insert({'user_id':user.id, 'type':[]})
            # article tag
            mdb_cont.db.article_tag.insert({'user_id':user.id, 'tag':[]})

            # email token
            confirm_url = url_for('online.confirm_email', token=token, _external=True)
            html = render_template('online/email/activate.html', confirm_url=confirm_url)

            # send email
            msg = Message("{}注册验证".format(config['email'].MAIL_PROJECT),
                          sender=config['email'].MAIL_DEFAULT_SENDER,
                          recipients=[email])
            msg.html = html
            send_email(mdb_sys.db, msg)
            flash({'type':'html','msg':config['email'].REGISTER_VER_HTML.format(
                user.email,
                url_for('online.resend_confirmation',email=user.email)
            )})
            _data['success'] = True
            return jsonify(_data)
        else:
            _data['flash'] = {'type':'w', 'msg':'邮箱格式不正确!'}

    # 验证码
    _code = create_code()
    _data['code'] = _code

    return jsonify(_data)

# --------------------------------------------------------------------------------------------------------
@api.route('/sign-in', methods=['POST'])
def sign_in():

    _data = login_sha(adm = False)
    return _data

# --------------------------------------------------------------------------------------------------------
@api.route('/adm/sign-in', methods=['POST'])
def adm_sign_in():
    _data = login_sha(adm = True)
    return _data

# --------------------------------------------------------------------------------------------------------
@api.route('/accounts/password-reset', methods=['POST'])
@login_required
def reset_password():
    _data = {}
    old_pass = request.form['old_password'].strip()
    pass1 = request.form['password'].strip()
    pass2 = request.form['password2'].strip()
    if pass1 != pass2:
        _data['flash'] = {'msg':'两次密码不一致!'}
        return jsonify(_data)
    _data = p_password_reset(old_pass, pass1)
    return jsonify(_data)

# --------------------------------------------------------------------------------------------------------
@api.route('/accounts/email-change', methods=['POST'])
@login_required
def email_change():
    _data = {}
    code = request.form['email_code'].strip()
    code_id = request.form['code_id']
    email = request.form['email'].strip()
    password = request.form['password'].strip()
    if not email:
        _data['flash'] = {'msg':'邮箱不能为空!'}
        return jsonify(_data)
    elif not ver_email(email):
        _data['flash'] = {'msg':'邮箱格式错误!'}
    elif not code:
        _data['flash'] = {'msg':'验证码错误'}
        return jsonify(_data)

    _data = p_email_change(code, code_id, email, password)
    return jsonify(_data)

# ---------------------------------------------------------------------------------------------------------
@api.route('/accounts/retrieve-password', methods=['POST'])
def retrieve_password():

    _data = {}
    code = request.form['email_code'].strip()
    code_id = request.form['code_id']
    email = request.form['email'].strip()
    password = request.form['password'].strip()
    password2 = request.form['password2'].strip()
    if not email:
        _data['flash'] = {'msg':'邮箱不能为空!'}
    elif not ver_email(email):
        _data['flash'] = {'msg':'邮箱格式错误!'}
    elif not code:
        _data['flash'] = {'msg':'验证码错误'}
    elif password != password2:
        _data['flash'] = {'msg':'两次密码不一致！'}
    else:
        _data = p_retrieve_password(email, code, code_id, password, password2)

    # 验证码
    _code = create_code()
    _data['code'] = _code
    return jsonify(_data)

# # --------------------------------------------------------------------------------------------------------
# @api.route('/accounts/edit-profile', methods=['POST'])
# @login_required
# def edit_profile():
#
#     username = request.form['username'].strip()
#     sex = request.form['sex']
#     addr = request.form['addr']
#     info = request.form['info'].strip()
#     avatar = request.form['avatar']
#     _data = user_edit_profile(avatar, username, sex, addr, info)
#     return jsonify(_data)

# --------------------------------------------------------------------------------------------------------
@api.route('/addr/data', methods=['GET'])
@login_required
def addr_data():
    _data = {}
    _data['addrs'] = addr_f()
    return jsonify(_data)

# --------------------------------------------------------------------------------------------------------
@api.route('/user/addr', methods=['GET'])
@login_required
def user_addr():
    _data = {}
    # 地址
    profile = mdb_user.db.user_profile.find_one_or_404({'user_id':current_user.id})
    addrs = addr_f()
    _provinces = ""
    _city = ""
    _area = ""
    addr = {'provinces':'', 'city':'', 'area':''}
    if 'provinces' in profile['addr'] and profile['addr']['provinces']:
        for lv in addrs:
            if lv['text'] == profile['addr']['provinces']:
                lv1 = lv
                _provinces = lv['id']
                addr["provinces"] = _provinces
                addr["provinces_n"] = profile['addr']['provinces']
                break

    if 'city' in profile['addr'] and profile['addr']['city']:
        for lv in lv1['children']:
            if lv['text'] == profile['addr']['city']:
                lv2 = lv
                _city = lv['id']
                addr['city'] = _city
                addr['city_n'] = profile['addr']['city']
                break
    if 'area' in profile['addr'] and profile['addr']['area']:
        for lv in lv2['children']:
            if lv['text'] == profile['addr']['area']:
                _area = lv['id']
                addr['area'] = _area
                addr['area_n'] = profile['addr']['area']
                break
    _data['addr'] = addr
    return jsonify(_data)

