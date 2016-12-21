#!/usr/bin/env python
#-*-coding:utf-8-*-
from flask import url_for, render_template, session, request
from flask_login import current_user, login_required, logout_user
from markupsafe import Markup
from werkzeug.utils import redirect
from apps import config
from apps.blueprint import online, base, admin
from apps.verify.process.ver_code import create_code

__author__ = 'woo'

# **********************************************************************************************************************
@base.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    view_data = {'login_type':'f'}
    Markup('''<meta property="qc:admins" content="14111676166677276375" />''')
    if current_user.is_authenticated:
        return redirect(url_for('base.index'))
    return render_template('{}/online/sign-in.html'.format(config['theme'].THEME_NAME),view_data=view_data)

# **********************************************************************************************************************
@admin.route('/woo', methods=['GET', 'POST'])
def sign_in():

    view_data = {'login_type':'c', 'title':'登录管理台'}
    if current_user.is_authenticated():
        return redirect(url_for('admin.index'))
    # 验证码
    _code = create_code()
    view_data['code'] = _code
    return render_template('{}/online/login.html'.format(config['theme'].THEME_NAME), view_data=view_data)


# *********************************************************************************************************************
@base.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    view_data = {'title':'注册-{}'.format(config['title'].TITLE)}

    # 验证码
    _code = create_code()
    view_data['code'] = _code
    return render_template('{}/online/user/sign-up.html'.format(config['theme'].THEME_NAME), view_data=view_data)

@base.route('/logout')
@login_required
def lsign_out():
    session.pop('qq_token', None)
    logout_user()
    return redirect(request.args.get('next') or url_for('base.index'))