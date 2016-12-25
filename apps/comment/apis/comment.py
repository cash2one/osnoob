#-*-coding:utf-8-*-
from apps import mdb_user, mdb_cont
from apps.blueprint import api
from apps.comment.process.comment import p_del_comment, p_comments, p_add_comment
from bson import ObjectId
from flask import request, jsonify
from flask_login import login_required, current_user

__author__ = 'woo'

# ----------------------------------------------------------------------------------------------------------------------
@api.route('/comments', methods=['GET','POST'])
def comments():

    post_id = request.args.get('post_id')
    c_filter = {'case_id':ObjectId(post_id), "$or":[{'status':1},{'status':2},{'status':3},{'status':5}]}
    view_data = p_comments(request, post_id, filter=c_filter)
    return jsonify(view_data)

# ----------------------------------------------------------------------------------------------------------------------
@api.route('/comment/add', methods=['POST'])
def add_comment():

    val = dict(request.form)
    if not "username" in val:
        val['username'] = [""]

    if not "email" in  val:
        val['email'] = [""]
    r = p_add_comment(val['username'][0], val['email'][0], val['case_id'][0], val['comment'][0], val['reply_id'][0])
    return jsonify(r)

# ----------------------------------------------------------------------------------------------------------------------
@api.route('/comment/delete', methods=['POST', 'DELETE'])
@login_required
def delete_comment():

    cid = request.form['cid']
    r = p_del_comment(cid, current_user.id)
    return jsonify(r)

# ----------------------------------------------------------------------------------------------------------------------
@api.route('/praise/add', methods=['POST'])
@login_required
def praise_add():

    case_id = request.form['post_id']
    _post = mdb_cont.db.posts.find_one({'_id':ObjectId(case_id)},{'praise_id':1})
    if current_user.id in _post['praise_id']:
        pass
    else:
        if current_user.is_authenticated():
            praise_id = current_user.id
        else:
            praise_id = request.remote_addr
        _post['praise_id'].append(praise_id)
        mdb_cont.db.posts.update({'_id':ObjectId(case_id)}, {'$set':{'praise_id':_post['praise_id']},"$inc":{"praise":1}})
    return jsonify({})

# ----------------------------------------------------------------------------------------------------------------------
@api.route('/praise/sub', methods=['POST'])
@login_required
def praise_sub():

    case_id = request.form['post_id']
    _post = mdb_cont.db.posts.find_one({'_id':ObjectId(case_id)},{'praise_id':1})
    if not current_user.id in _post['praise_id']:
        pass
    else :
        if current_user.is_authenticated():
            praise_id = current_user.id
        else:
            praise_id = request.remote_addr
        _post['praise_id'].remove(praise_id)
        mdb_cont.db.posts.update({'_id':ObjectId(case_id)}, {'$set':{'praise_id':_post['praise_id']},"$inc":{"praise":-1}})
    return jsonify({})