#-*-coding:utf-8-*-
from apps.config import Permission
from apps.online.process.user import post_cnt_update
from apps.post.process.post import p_posts
from bson import ObjectId
from apps import mdb_user, config, mdb_cont
from apps.blueprint import api
from flask import request, jsonify
from flask_login import current_user, login_required
from werkzeug.exceptions import abort
from apps.shared_tools.region.osn_format import request_path

__author__ = 'woo'

# ******************************************************************************************************
@api.route('/posts', methods=['GET', 'POST'])
def posts():
    '''
    文章api查询
    :return:
    '''
    request_path(['sub','user_id','type','tag'])
    sub = request.args.get('sub')
    user_id = request.args.get('user_id')
    type = request.args.get('type')
    tag = request.args.get('tag')
    sort_f = [('time',-1)]
    if user_id:
        if sub == "draft" or sub == "review":
            if current_user.is_anonymous() or (int(user_id) != current_user.id and not current_user.can(Permission.ADMINISTER)):
                abort(404)
        filter = {'user_id':int(user_id)}
    else:
        filter = {'subject':{'$ne':'sys'}}
    if type:
        filter['type'] = type
    elif tag:
        filter['tag'] = type

    if sub == 'hot':
        sort_f = [('praise',-1),('pv',-1)]
        filter['status'] = 1
    elif sub == "draft":
        filter['status'] = 0
    elif sub == "review":
        filter['$or'] = [{'status':2},{'status':3},{'status':5}]
    elif sub=="new":
        filter['status'] = 1
        if not user_id:
            filter['pv'] = {"$gte":config['post'].NEW_PV}

    else:
        filter['status'] = 1
        filter['subject'] = sub
        filter['pv'] = {"$gte":config['post'].NEW_PV}
    view_data = p_posts(request, sort = sort_f,filter=filter)
    if user_id:
        for data in view_data['posts']:
            if data['status'] == 3:
                data['title'] = '{}<span  style="color: #ea1717; display: inline;" >[不通过]</span>'.format(data['title'])
    return jsonify(view_data)


# ******************************************************************************************************
@api.route('/posts/type', methods=['GET', 'POST'])
def posts_type():
    request_path(['type','tag'])
    type = request.args.get('type')
    tag = request.args.get('tag')
    if type:
        filter = {'status':1, 'type':type}
    elif tag:
        filter = {'status':1, 'tag':tag}
    view_data = p_posts(request, filter=filter)

    return jsonify(view_data)


# ******************************************************************************************************
@api.route('/posts/subject', methods=['GET', 'POST'])
def posts_subject():
    request_path(['subject'])
    subject = request.args.get('subject')
    filter = {'status':1, 'subject':subject}
    view_data = p_posts(request, filter=filter)
    return jsonify(view_data)

# ******************************************************************************************************
@api.route('/post', methods=['GET', 'POST'])
def post():

    view_data = {}
    post_id = request.args.get('p_id')
    # 查询
    view_data['post'] = mdb_cont.db.posts.find_one_or_404({'_id':ObjectId(post_id), 'status':1})
    view_data['username'] = mdb_user.db.user.find({"id":view_data['post']['user_id']})
    
    return jsonify(view_data)

# ******************************************************************************************************
@api.route('/post/delete', methods=['POST'])
@login_required
def post_del():
    post_id = request.form['pid']
    mdb_cont.db.posts.update({'_id':ObjectId(post_id), 'user_id':current_user.id}, {'$set':{'status':4}})
    post_cnt_update(current_user.id)
    return jsonify({})

# --------------------------------------------------------------------------------------------------------
@api.route('/post/add-tag', methods=['POST'])
@login_required
def add_tag():

    _data = {'flash':None}
    ag_list = request.form['tag'].strip()
    tags = mdb_cont.db.tag.find_one({'user_id':current_user.id})
    tags_sys = mdb_cont.db.tag.find_one({'user_id':0})
    tag_list_t = ag_list.replace("；", ";").split(';')
    tag_list = []
    for tag in tag_list_t:
        if not tag:
            continue
        if len(tag.strip().encode("gbk").decode("gbk")) > 15 or len(tag.strip().encode("gbk").decode("gbk"))<2:
            _data['flash'] = {'msg':u'标签最少2个字,最多15个字!','type':'w'}
        elif ',' in tag.strip() or "，" in tag.strip() or ";" in tag.strip() or "；" in tag.strip():
            _data['flash'] = {'msg':u'标签最少2个字,最多15个字,不能有逗号','type':'w'}
        elif tags and tags_sys and not tag.strip() in tags['tag'] and not tag.strip() in tags_sys['tag']:
            tag_list.append(tag.strip())
    if tags:
        tags['tag'].extend(tag_list)
        mdb_cont.db.tag.update({'user_id':current_user.id}, {'$set':{'tag':tags['tag']}})
    else:
        mdb_cont.db.tag.insert({'user_id':current_user.id, 'tag':tag_list, 'subject':''})
    _data['tags'] = tag_list
    return jsonify(_data)

# --------------------------------------------------------------------------------------------------------
@api.route('/post/del-tag', methods=['POST'])
@login_required
def del_tag():

    _data = {'flash':None}
    tag_list = request.form['tag'].split(',')
    tags = mdb_cont.db.tag.find_one({'user_id':current_user.id})
    tags_sys = mdb_cont.db.tag.find_one({'user_id':0})
    if tags:
        tags = tags['tag']
        for tag in tag_list:
            if tag.strip() in tags:
                tags.remove(tag.strip())
            elif tag.strip() and tag.strip() in tags_sys['tag']:
                _data['flash'] = {'msg':'系统标签不能删除!'}

    mdb_cont.db.tag.update({'user_id':current_user.id}, {'$set':{'tag':tags}})
    return jsonify(_data)


# # ---------------------------------------------------------------------------------------------------------------
# #暂时不使用
# @api.route('/post/user-tag-type', methods=['GET'])
# @login_required
# def post_user_tag_type():
#
#     _data = {}
#     sub = request.args.get('sub')
#     _data['tags'] = []
#     tags = mdb_cont.db.tag.find_one({'user_id':0})
#     if tags:
#         _data['tag_s'] = tags['tag']
#     _data['tag_u'] = []
#     tags = mdb_cont.db.tag.find_one({'user_id':current_user.id})
#     if tags:
#         _data['tag_u'] = tags['tag']
#
#     _data['types'] = mdb_cont.db.post_type.find_one({'subject':sub})['type']
#     return jsonify(_data)
#
#
# # ---------------------------------------------------------------------------------------------------------------
# #暂时不使用
# @api.route('/post/add', methods=['POST'])
# @login_required
# def add_post():
#     _data = {}
#     print request.form
#     subject = request.form['sub']
#     issue = request.form['issue']
#     draft = request.form['draft']
#     title = request.form['title']
#     s_type = request.form['s_type']
#     body = request.form['body']
#     tag_list = request.form['tag_list']
#     if not title:
#         _data['flash'] = {'msg':'标题不能为空!', 'type':'w'}
#         return jsonify(_data)
#     elif not body:
#         _data['flash'] = {'msg':'不能为空!', 'type':'w'}
#         return jsonify(_data)
#     _data = p_post_add(subject, issue, draft, title, s_type, body, tag_list)
#     return jsonify(_data)




