#!/usr/bin/env python
#-*-coding:utf-8-*-
from flask import url_for, render_template, session, request, flash
from flask_login import current_user, login_required, logout_user
from markupsafe import Markup
import time
from werkzeug.utils import redirect
from apps import config, mdb_user
from apps.blueprint import online, base, admin
from apps.online.forms.user import EditRewardForm
from apps.online.process.user import user_edit_profile
from apps.shared_tools.image.image_up import img_del, img_up
from apps.verify.process.ver_code import create_code

__author__ = 'woo'

# **********************************************************************************************************************
@base.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    view_data = {'login_type':'f', 'title':'Sign in'}
    Markup('''<meta property="qc:admins" content="14111676166677276375" />''')
    if current_user.is_authenticated:
        return redirect(url_for('base.index'))
    return render_template('{}/online/sign-in.html'.format(config['theme'].THEME_NAME), view_data=view_data)

# **********************************************************************************************************************
@admin.route('/woo', methods=['GET', 'POST'])
def sign_in():

    view_data = {'login_type':'c', 'title':'登录管理台'}
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    # 验证码
    _code = create_code()
    view_data['code'] = _code
    return render_template('{}/online/sign-in.html'.format(config['theme'].THEME_NAME), view_data=view_data)

# *********************************************************************************************************************
@base.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    view_data = {'title':'注册-{}'.format(config['title'].TITLE)}

    # 验证码
    _code = create_code()
    view_data['code'] = _code
    return render_template('{}/online/user/sign-up.html'.format(config['theme'].THEME_NAME), view_data=view_data)

@base.route('/sign_out')
@login_required
def sign_out():
    session.pop('qq_token', None)
    logout_user()
    return redirect(request.args.get('next') or url_for('base.index'))


@online.route('/accounts', methods=['GET','POST'])
@login_required
def account():
    view_data = {'title':'个人信息-{}'.format(config['title'].TITLE)}
    if request.method == 'POST':
        uploaded_files = request.files.getlist("avatar")
        username = request.form['username'].strip()
        try:
            sex = request.form['sex']
        except:
            sex = None

        addr = {'p':request.form['p'], 'c':request.form['c'], 'a':request.form['a']}
        info = request.form['info'].strip()
        user_edit_profile(uploaded_files, username, sex, addr, info)
        return redirect(url_for('online.account'))

    profile = mdb_user.db.user_profile.find_one_or_404({'user_id':current_user.id})
    # 头像
    view_data['ava_url'] = profile['avatar_url']
    # 姓名
    view_data["username"] = current_user.username
    view_data["user_domain"] = profile['user_domain']
    view_data['email'] = profile['email'].strip()
    if view_data['email'] in config['oauth_login'].EMAIL_LIST:
        view_data['email'] = u"第三方账号登录,请先修改邮箱"

    if 'sex' in profile:
        if profile['sex'] == 0:
            view_data["m"] = True
        elif profile['sex'] == 1:
            view_data["f"] = True
    view_data['info'] = profile['info'].strip()
    return  render_template('online/user/user.html', view_data=view_data)


@online.route('/accounts/password-reset', methods=['GET', 'POST'])
@login_required
def password_reset():

    if current_user.email.strip() in config['oauth_login'].EMAIL_LIST:
        flash({"msg":u"请先绑定邮箱, 用于找回密码！", "type":'w'})
        return redirect(url_for("online.account"))

    view_data = {'title':'密码修改-{}'.format(config['title'].TITLE)}
    profile = mdb_user.user_profile.find_one_or_404({'user_id':current_user.id})
    if 'is_oauth_first_change' in profile and profile['is_oauth_first_change']:
        view_data['is_oauth_first_change'] = True
    return render_template('online/user/password_reset.html', view_data=view_data)


# User levels: edit user data*******************************************************************************************
@online.route('/accounts/pre-email-change', methods=['GET', 'POST'])
@login_required
def email_change():

    view_data = {'title':'邮箱修改-{}'.format(config['title'].TITLE)}
    return  render_template('online/user/email_change.html',  view_data=view_data)


# User levels: edit user data*******************************************************************************************
@online.route('/accounts/retrieve-password', methods=['GET', 'POST'])
def retrieve_password():

    view_data = {'title':'找回密码-{}'.format(config['title'].TITLE)}
    # 验证码
    _code = create_code()
    view_data['code'] = _code

    return  render_template('online/user/ret_password.html', view_data=view_data)

# ------------------------------------------------------------------------------------------------------
@online.route('/accounts/reward', methods=['GET', 'POST'])
@login_required
def reward():
    view_data = {'title':'打赏-{}'.format(config['title'].TITLE)}
    profile = mdb_user.user_profile.find_one_or_404({'user_id':current_user.id})
    if 'pay' in profile and profile['pay']:
        view_data['pay'] = profile['pay']
        pay_cnt = 0
        for k in profile['pay']:
            if "url" in profile['pay'][k]:
                pay_cnt += 1
        view_data['pay_cnt'] = pay_cnt
    else:
        view_data['pay'] = {}
        view_data['pay_cnt'] = 0
    return  render_template('online/user/reward.html', view_data=view_data)

# ------------------------------------------------------------------------------------------------------
@online.route('/accounts/reward/add', methods=['GET', 'POST'])
@login_required
def reward_add():
    view_data = {'title':'添加打赏-{}'.format(config['title'].TITLE)}
    profile = mdb_user.user_profile.find_one_or_404({'user_id':current_user.id})
    form = EditRewardForm('add')
    if form.submit.data:
        if current_user.verify_password(form.password.data):
            bucket_name = {'b':config['upload'].IMG_B, 'domain':'img', 'project':'pay'}
            uploaded_files = request.files.getlist("payimg")
            r = img_up(uploaded_files, bucket_name)
            if r['url'] != -1 and r['url'] != 1:
                if 'pay' in profile and profile['pay']:
                    _pay = profile['pay']
                    _pay[form.pay_type.data] = {'url':r['url'], 'word':form.word.data.strip(), 'status':0, 'time':time.time()}
                else:
                    _pay = {form.pay_type.data:{'url':r['url'], 'word':form.word.data.strip(), 'status':0, 'time':time.time()}}
                flash({'msg':'二维码上传成功,需要等待审核！', 'type':'s'})
            else:
                flash({'type':'e', 'msg':'支付二维码上传失败!'})
                return  render_template('online/user/reward_edit.html', view_data=view_data, form=form)

            _pay[form.pay_type.data]['use'] = int(form.nonuse.data)
            _pay[form.pay_type.data]['time'] = time.time()
            mdb_user.user_profile.update({'user_id':current_user.id}, {'$set':{'pay':_pay}})
            return  redirect(url_for('online.reward'))
        else:
            flash({'msg':'登录密码不对!', 'type':'e'})

    view_data['pay_url'] = {}
    return  render_template('online/user/reward_edit.html', view_data=view_data, form=form)


# ------------------------------------------------------------------------------------------------------
@online.route('/accounts/reward/edit/<type>', methods=['GET', 'POST'])
@login_required
def reward_edit(type):
    view_data = {'title':'打赏设置-{}'.format(config['title'].TITLE)}
    profile = mdb_user.user_profile.find_one_or_404({'user_id':current_user.id})
    form = EditRewardForm('edit')
    if form.submit.data:
        if current_user.verify_password(form.password.data):
            bucket_name = {'b':config['upload'].IMG_B, 'domain':'img', 'project':'pay'}
            uploaded_files = request.files.getlist("payimg")
            r = img_up(uploaded_files, bucket_name)
            if r['url'] != -1 and r['url'] != 1:
                img_del(profile['pay'][type.strip()]['url'])
                if 'pay' in profile:
                    _pay = profile['pay']
                    _pay[type.strip()] = {'url':r['url'], 'word':form.word.data.strip(), 'status':0, 'time':time.time()}
                else:
                    _pay = {type.strip():{'url':r['url'], 'word':form.word.data.strip(), 'status':0, 'time':time.time()}}
                flash({'msg':'修改了二维码,需要等待审核！', 'type':'s'})
            else:
                if 'pay' in profile:
                    _pay = profile['pay']
                    status = _pay[type.strip()]['status']
                    _pay[type.strip()] = {'url':_pay[type.strip()]['url'], 'word':form.word.data.strip(), 'status':status}
                else:
                    _pay = {type.strip():{'url':'', 'word':form.word.data.strip(), 'status':0}}
            _pay[type.strip()]['use'] = int(form.nonuse.data)
            _pay[type.strip()]['time'] = time.time()
            mdb_user.user_profile.update({'user_id':current_user.id}, {'$set':{'pay':_pay}})
            return  redirect(url_for('online.reward'))
        else:
            flash({'msg':'登录密码不对!', 'type':'e'})

    form.pay_type.data = type.strip()
    form.word.data = profile['pay'][type.strip()]['word']
    form.nonuse.data = str(profile['pay'][type.strip()]['use'])
    view_data['pay_url'] = profile['pay'][type.strip()]['url']
    view_data['op_type'] = 'edit'
    return  render_template('online/user/reward_edit.html', view_data=view_data, form=form)