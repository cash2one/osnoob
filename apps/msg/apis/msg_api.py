#-*-coding:utf-8-*-
from apps.blueprint import api
from apps.msg.process.msgs import sta_msg, p_msgs, sta_msg_all, del_msg
from flask import jsonify, request, flash
from flask_login import current_user

__author__ = 'woo'

@api.route('/msg/status', methods=['POST'])
def msg_status():
    id = request.form['id']
    sta_msg(id, current_user.id, status=1)
    return jsonify({})

@api.route('/msg/status/all', methods=['POST'])
def msg_status_all():
    sta_msg_all(current_user.id, status=1)
    return jsonify({})

@api.route('/msg/delete', methods=['POST'])
def msg_del():
    view_data = {}
    id = request.form['id']
    if id:
        sta_msg(id, current_user.id, status=2)
    else:
        view_data = {'msg':u'系统错误!删除失败!', 'type':'e'}
    return jsonify(view_data)

# ******************************************************************************************************
@api.route('/msgs', methods=['GET', 'POST'])
def msgs():
    sub = request.args.get('sub')
    user_id = request.args.get('user_id')
    sta = request.args.get('sta')
    filter ={'user_id':int(user_id), 'sub':{'$ne':'sys'}, 'status':0, 'case_status':1}
    if sub:
        filter['sub'] = sub
    if sta == "unread":
        filter['status'] = 0
    if sta == "read":
        filter['status'] = 1
    view_data = p_msgs(request, filter = filter, pre=5)
    return jsonify(view_data)


