#-*-coding:utf-8-*-
from apps import mdb_user
from apps.blueprint import  online
from flask import url_for, request
from flask_login import login_required, current_user
from werkzeug.utils import redirect

__author__ = 'woo'

# **********************************************************************************************************************
@online.route('/clear/all-msg', methods=['GET', 'POST'])
@login_required
def clear_msg():

    # remove msg
    mdb_user.db.user_msg.remove({'to':current_user.id})

    return redirect(request.args.get('next') or url_for('admin.index'))





