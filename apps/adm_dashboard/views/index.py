#-*-coding:utf-8-*-
from apps.config import config
from apps import mdb_user, mdb_cont
from apps.config import Permission
from apps.shared_tools.decorator.decorators import permission_required
from apps.verify.process.ver_code import create_code
from flask import render_template, redirect, url_for,  abort

#
from flask_login import current_user, login_required
from apps.blueprint import admin

__author__ = 'woo'

@admin.route('/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ECP)
def index():

    return redirect(url_for('admin.dashboard'))

@admin.route('/dashboard', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ECP)
def dashboard():
    view_data = {}
    return render_template('{}/home/dashboard.html'.format(config["theme"].ADM_THEME_NAME), view_data=view_data)


@admin.route('/chart', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ECP)
def chart():

    view_data = {'title':'报表-管理台'}
    if current_user.is_delete or not current_user.active:
        return redirect(url_for('online.login'))
    elif not current_user.can(Permission.ADMINISTER) and not current_user.is_role(Permission.ECP):
        return redirect(url_for('admin.posts_management'))

    view_data['user_cnt'] = mdb_user.db.user.count()
    view_data['post_cnt'] = mdb_cont.db.posts.count()
    return render_template('{}/home/chart.html'.format(config["theme"].ADM_THEME_NAME), view_data=view_data)


@admin.route('/audit', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.AUDITOR)
def audit():
    abort(404)



