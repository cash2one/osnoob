# -*-coding:utf-8-*-
import re
from bson import ObjectId
from flask import url_for, request, jsonify, flash
from flask_login import current_user, login_user, logout_user
import time
from apps import mdb_user, config, mdb_sys, mdb_cont
from apps.config import Permission
from apps.online.process.user_verify import User
from apps.shared_tools.image.image_up import img_up, img_del
from apps.shared_tools.region.addr_format import addr_f
from apps.verify.process.email_code import verify_email_code
from apps.verify.process.email_format import is_email
from apps.verify.process.ver_code import verify_code, vercode_del, create_code

__author__ = 'woo'

# 登录-------------------------------------------------------------------------------------
def login_sha(adm = False):
    _data = {}
    if current_user.is_authenticated():
        _data['success'] = True
        _data['url'] = request.args.get('next') or url_for('online.index')
        return jsonify(_data)
    
    # code
    username = request.value.all('username').strip()
    password = request.value.all('password').strip()
    code = request.value.all('vercode').strip()
    code_url = request.value.all('code_url').strip()
    remember_me = request.value.all('remember_me')
    r = verify_code(code_url, code)
    vercode_err = False
    if not r:
        vercode_err = True
        vercode_del(code_url)

    # name & pass
    if "." in username and '@' in username:
        user = mdb_user.db.user.find_one({"email":username})
    else:
        user = mdb_user.db.user.find_one({"username":username})
    user = User(user)
    is_continue = False
    if user and adm:
        if user.can(Permission.ADMINISTER):
            is_continue = True

    elif user:
        if not user.can(Permission.ADMINISTER):
            is_continue = True
    if is_continue:
        # 如果验证码错误那就判断用户是否已经３次输错密码
        if vercode_err:
            user_p = mdb_user.db.user_profile.find_one({'user_id':user.id})
            if user_p and 'pass_error' in user_p and user_p['pass_error'] >= 5:
                _data['flash'] = {'msg':'验证码错误！', 'type':'e'}
                # 验证码
                _code = create_code()
                _data['code'] = _code
                return jsonify(_data)

        # 密码验证
        if is_continue and user and user.verify_password(password) and not user.is_delete:

            if user.is_active():
                login_user(user, remember_me)
                mdb_user.db.user_profile.update({'user_id':current_user.id}, {"$set":{"pass_error":0}})
                # Record the info
                login_info = {
                    'last_login_time':time.time(),
                    'last_login_ip':request.remote_addr,
                }
                mdb_user.db.user_profile.update({'user_id':current_user.id}, {'$set':login_info})

                _data['success'] = True
                return jsonify(_data)

            # 未激活
            _data['flash'] = {'type':'html','msg':config['email'].VER_HTML.format(
                        username,
                        url_for('online.resend_confirmation',email = user.email)
            )}
            # 验证码
            _code = create_code()
            _data['code'] = _code
            return jsonify(_data)
        #　密码错误
        _data = need_vercode(user.id)
        _data['flash'] = {'type':'e','msg':u'帐号或密码错误哦！'}

    else:
        _data['flash'] = {'type':'e','msg':u'帐号或密码错误哦！'}
    return jsonify(_data)

# 判断是否需要验证码 -------------------------------------------------
def need_vercode(user_id):
    _data = {}
    mdb_user.db.user_profile.update({'user_id':user_id}, {"$inc":{"pass_error":1}})
    user_p = mdb_user.db.user_profile.find_one({'user_id':user_id})
    if user_p and ("pass_error" in user_p) and user_p['pass_error'] >= 5:
        _code = create_code()
        _data['code'] = _code
    return _data

# 用户密码修改　-------------------------------------------------------
def p_password_reset(old_pass, new_pass):

    _data = {}

    r = password_format(new_pass)
    if 'flash' in r:
        return r

    user = mdb_user.db.user.find_one({"_id":ObjectId(current_user.id)})

    profile = mdb_user.db.user_profile.find_one_or_404({'user_id':current_user.id})
    if 'is_oauth_first_change' in profile and profile['is_oauth_first_change']:
        is_oauth_first_change = True
    else:
        is_oauth_first_change = False
    if (user and current_user.verify_password(old_pass)) or (user and is_oauth_first_change):
        new_password_hash = current_user.password(new_pass)
        mdb_user.db.user.update({"_id":current_user.id}, {"$set":{"password":new_password_hash}})

        # log
        mdb_user.db.user_op_log.insert({'user_id':current_user.id,
                                   'op_type':'setpass',
                                   'time':time.time(),
                                   'status':'s',
                                   'info':'',
                                   'ip':request.remote_addr
                                   })
        #
        flash({'msg':'密码修改成功,请重新登录哦！','type':'s'})
        logout_user()
        _data['url'] = url_for('online.login')
        return _data

    # log
    mdb_user.db.user_op_log.insert({'user_id':current_user.id,
                               'op_type':'setpass',
                               'time':time.time(),
                               'status':'f',
                               'info':'密码错误',
                               'ip':request.remote_addr,
                               })
    _data['flash'] = {'msg':'原密码错误！','type':'e'}

    return _data

# 密码规格验证-----------------------------------------------------------------------------
def password_format(password):

    _data = {}
    if len(password) < 8 :
        _data['flash'] = {'type':'w','msg':u'密码至少8个字符！并至少包含数字,字母,特殊字符的两种'}
    else:
        too_simple = True
        last_ac = False
        for p in password:
            _ac = ord(p)
            if last_ac:
                if _ac != last_ac+1:
                    too_simple = False
                    break
            last_ac = _ac
        if too_simple:
            _data['flash'] = {'type':'w','msg':u'密码太简单,不能取连续字符！'}
    return _data

# 邮箱修改 ------------------------------------------------------------------------------------
def p_email_change(code, code_id, email, password):

    _data = {}
    r = verify_email_code(code_id, code)
    if not r:
        _data['flash'] = {'msg':'验证码错误！', 'type':'e'}
    else:
        if is_email(email):
            is_oauth_first_change = current_user.email.strip() in config['oauth_login'].EMAIL_LIST
            if current_user.verify_password(password) or is_oauth_first_change:
                mdb_user.db.user.update({"_id":current_user.id},
                                        {"$set":{"email":email, "update_time":time.time()}})

                up = {'email':email}
                if is_oauth_first_change:
                    up['is_oauth_first_change'] = True
                mdb_user.db.user_profile.update({'user_id':current_user.id}, {'$set':up})
                # log
                mdb_user.db.user_op_log.insert({'user_id':current_user.id,
                                           'op_type':'setemail',
                                           'time':time.time(),
                                           'status':'s',
                                           'info':'',
                                           'ip':request.remote_addr
                                           })
                #
                flash({'msg':'邮箱Email修改成功！', 'type':'s'})
                _data['url'] = url_for('online.account')
                return _data
            else:
                # log
                mdb_user.db.user_op_log.insert({'user_id':current_user.id,
                                           'op_type':'setemail',
                                           'time':time.time(),
                                           'status':'f',
                                           'info':'密码错误',
                                           'ip':request.remote_addr
                                           })
                #
                _data['flash']= {'msg':'登录密码不对哦！', 'type':'e'}
        else:
            _data['flash']= {'msg':'邮件格式不合法！', 'type':'w'}

    return _data

# 找回密码 -------------------------------------------------------------------------------------------------------------
def p_retrieve_password(email, code, code_id, password, password2):

    _data = {}
    user = mdb_user.db.user.find_one({"email":email})
    if user:
        r = verify_email_code(code_id, code)
    else:
        _data['flash'] = {'msg':'账号不存在!', 'type':'e'}
        return _data
    if not r:
        # log
        mdb_user.db.user_op_log.insert({'user_id':None,
                                   'email':email,
                                   'op_type':'retrieve_pass',
                                   'time':time.time(),
                                   'status':'f',
                                   'info':'邮箱/短信验证码错误',
                                   'ip':request.remote_addr
                                   })
        #
        _data['flash'] = {'msg':'邮件或短信验证码错误！', 'type':'e'}
    else:

        if user:
            r = password_format(password)
            if 'flash' in r:
                return r
            elif password != password2:
                _data['flash'] = {'msg':'两次密码不一致！','type':'w'}
            else:
                user = User(user)
                mdb_user.db.user.update({"_id":user["_id"]},
                                        {"$set":{"password":user.password(password)}})

                flash({'msg':'密码重设成功,请注意保管！','type':'s'})
                logout_user()
                _data['url'] = url_for('online.login')
                return _data

    return _data
# ---------------------------------------------------------------------------------------------------------------------
# 用户信息
def p_user(user_id, level=1):

    profile = mdb_user.db.user_profile.find_one({'user_id':user_id})
    if not 'pay' in profile or profile['pay']== []:
        profile['pay'] = {'use':0}
    else:
        if not 'alipay' in profile['pay']:
            profile['pay']['alipay'] = {'status':0}
        if not 'wechatpay' in profile['pay']:
            profile['pay']['wechatpay'] = {'status':0}
    return profile

# 用户文章更新统计
def post_cnt_update(user_id):

    # 更新统计
    post_cnt = mdb_cont.db.article.find({'user_id':user_id, 'status':1}).count()
    mdb_user.db.user_profile.update({'user_id':user_id}, {'$set':{'post_cnt':post_cnt}})

# ---------------------------------------------------------------------------------------------------------------------
def user_edit_profile(uploaded_files, username, sex, addr, info):
    _data = {}
    domain = None
    if 'u-domain' in request.value.all and request.value.all['u-domain'].strip():
        names = mdb_sys.db.audit_rules.find_one({'type':'username'})
        domain = request.value.all['u-domain'].strip().replace(' ','')
        if len(domain)<3 or len(domain)>30:
            flash({'msg':'个性域名:需要3至30个字符!', 'type':'w'})
            return jsonify(_data)
        if not re.search(r"^[a-z0-9]+$",domain):
            flash({'msg':'个性域名:只能是数字, 小写字母!', 'type':'w'})
            return jsonify(_data)

        elif mdb_user.db.user_profile.find_one({'domain':domain}) or domain==str(current_user.id):
            flash({'msg':'此个性域名已被使用!', 'type':'w'})
            return jsonify(_data)
        elif domain in names and not current_user.can(Permission.ADMINISTER) and not current_user.is_role(Permission.ECP):
            flash({'msg':'此个性域名已被使用!', 'type':'w'})
            return jsonify(_data)

    if not username:
        flash({'msg':'名号不能为空!', 'type':'w'})
        return jsonify(_data)

    user = mdb_user.db.user.find_one({"username":username})
    if user and user["_id"] != current_user.id:
        flash({'msg':'此名号已被使用!', 'type':'w'})
        return jsonify(_data)

    names = mdb_sys.db.audit_rules.find_one({'type':'username'})
    try:
        t_username = username.upper()
    except:
        t_username = username
    if t_username in names['rule'] and not current_user.can(Permission.ADMINISTER) and not current_user.is_role(Permission.ECP):
        flash({'msg':'此名号已被使用!', 'type':'w'})
        return jsonify(_data)

    if len(username.encode("gbk").decode("gbk")) > 150:
        flash({'msg':u'最多150字哦!','type':'w'})
        return jsonify(_data)

    # ---------------------------------------------------------------
    tel = ""

    # 地址
    _provinces = ''
    _city = ''
    _area = ''
    addrs = addr_f()
    if addr['p'].strip("string:"):
        for lv in addrs:
            if lv['id'] == addr['p'].strip("string:"):
                lv1 = lv
                _provinces = lv['text']
                break
    if addr['c'].strip("string:"):
        for lv in lv1['children']:
            if lv['id'] == addr['c'].strip("string:"):
                lv2 = lv
                _city = lv['text']
                break
    if addr['a'].strip("string:"):
        for lv in lv2['children']:
            if lv['id'] == addr['a'].strip("string:"):
                _area = lv['text']
                break
    addr = {"provinces":_provinces}
    addr['city'] = _city
    addr['area'] = _area
    #性别
    if sex:
        sex = int(sex)
    # 头像
    bucket_name = {'b':config['upload'].AVA_B, 'domain':'avatar', 'project':'avatar'}
    r = img_up(uploaded_files, bucket_name)
    if r['url'] != -1:
        if r['url'] == 1:
            user_profile = {
            'username':username,
            'addr':addr,
            'info':info,
            'tel_num':tel,
            'sex':sex
            }
        else:
            user_profile = {
                'username':username,
                'addr':addr,
                'info':info,
                'tel_num':tel,
                'sex':sex,
                'avatar_url':r['url']
            }
            u_p = mdb_user.db.user_profile.find_one({'user_id':current_user.id})
            if u_p:
                if not 'default' in u_p['avatar_url']['key']:
                    img_del(u_p['avatar_url'])
        flash({'msg':'头像更改成功,2秒后更新!.','type':'s'})
    else:
        user_profile = {
            'username':username,
            'addr':addr,
            'info':info,
            'tel_num':tel,
            'sex':sex
            }

    mdb_user.db.user.update({"_id":current_user.id}, {"$set":{"username":username}})
    if domain:
        user_profile['user_domain'] = domain
        user.domain = domain
    mdb_user.db.user_profile.update({'user_id':current_user.id}, {'$set':user_profile})
    flash({'msg':'信息修改成功哦.','type':'s'})

    return _data
