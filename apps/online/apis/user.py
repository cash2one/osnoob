#-*-coding:utf-8-*-
from flask import url_for, request, jsonify, render_template, flash
from flask_login import login_required, current_user
from random import randint
from flask_mail import Message
import time
from apps import mdb, config, db, mdb_sys
from apps.admin.models.user import User, Permission, Role
from apps.blueprint import api
from apps.online.process.user import login_sha, p_password_reset, password_format, p_email_change, p_retrieve_password
from apps.shared_tool.addr_format import addr_f
from apps.shared_tool.email.email_format import ver_email
from apps.shared_tool.email.send_email import send_email
from apps.shared_tool.email.token import generate_confirmation_token
from apps.verify.process.email_format import is_email
from apps.verify.process.ver_code import verify_code, vercode_del, create_code

# --------------------------------------------------------------------------------------------------------
@api.route('/sign-up', methods=['POST'])
def sign_up():

    _data = {'flash':None}
    role_id = Role.query.filter_by(permissions=Permission.AVERABGEUSER).first().id
    # code
    email = request.form['email'].strip()
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    password2 = request.form['password2'].strip()
    code = request.form['vercode'].strip()
    code_url = request.form['code_url']
    r = verify_code(code_url, code)
    if not ver_email(email):
        _data['flash'] = {'msg':'邮箱格式错误！', 'type':'e'}
    elif not r:
        _data['flash'] = {'msg':'验证码错误！', 'type':'e'}
        vercode_del(code_url)
    elif password2 != password:
        _data['flash'] = {'msg':'两次密码不一致！', 'type':'e'}
    elif User.query.filter_by(email=email).first():
        _data['flash'] = {'type':'w','msg':u'此邮箱已在该网站注册过哦，请直接登录！'}
    elif User.query.filter_by(username=username).first():
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
            user = User(username=username,
                        email=email,
                        password=password,
                        role_id=role_id,
                        )
            db.session.add(user)
            db.session.commit()

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
            mdb.db.user_profile.insert(user_profile)
            # post type
            mdb.db.post_type.insert({'user_id':user.id, 'type':[]})
            # post tag
            mdb.db.tag.insert({'user_id':user.id, 'tag':[]})

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
    profile = mdb.db.user_profile.find_one_or_404({'user_id':current_user.id})
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

