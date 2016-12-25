#-*-coding:utf-8-*-
import time
from apps import mdb_user, config
from apps.blueprint import people
from apps.msg.process.msgs import p_msgs
from flask import request, render_template
from flask_login import login_required, current_user

__author__ = 'woo'

@people.route('/msg', methods=['GET', 'POST'])
@login_required
def msg_management():

    subject = request.args.get('subject')
    sta = request.args.get('sta')
    filter ={'user_id':current_user.id, 'sub':{'$ne':'sys'}, 'status':0, 'case_status':{'$ne':0}}
    if subject:
        filter['sub'] = subject
    if sta == "unread":
        filter['status'] = 0
    if sta == "read":
        filter['status'] = 1

    view_data = p_msgs(request, filter = filter, pre=5)
    view_data['profile'] = mdb_user.db.user_profile.find_one_or_404({'user_id':current_user.id})
    view_data['title'] = u'消息-{}'.format(config['title'].TITLE)
    return render_template('people/msgs.html',  view_data=view_data)


