# -*-coding:utf-8-*-
from kombu import uuid
from apps import mdb_user, config, mdb_cont
from apps.blueprint import post
from apps.comment.process.comment import p_comments
from apps.post.process.post import post_tags, post_types, recommend_posts, p_posts, p_post, p_post_pv_1
from bson import ObjectId
from flask import render_template, request, redirect, url_for, make_response
from flask_login import current_user, login_required
from werkzeug.exceptions import abort

@post.route('/<post_id>', methods=['GET', 'POST'])
def show(post_id):

    '''
    comment status
    1:通过
    2:待审核
    ３:未通过
    ４：已删除
    5:自动审核通过
    :return:
    '''
    
    # post
    view_data = p_post(filter={'_id':ObjectId(post_id), 'status':1})
    if "redirect" in view_data:
        return redirect(view_data['redirect'])
    if not current_user.is_anonymous():
        if current_user.id in view_data['post']['praise_id']:
            view_data['praise_status'] = True

    # comment
    c_filter = {'case_id':ObjectId(post_id), "$or":[{'status':1},{'status':2},{'status':3},{'status':5}]}
    view_data = dict(view_data, **p_comments(request, post_id, filter=c_filter))

    # 侧边栏
    # 推荐
    sort_f = [('praise',-1),('pv',-1)]
    filter = {'status':1, 'type':view_data['post']['type'],'_id':{'$ne':ObjectId(post_id)}}
    view_data['recommend'] = recommend_posts(sort=sort_f, filter=filter)
    # 标签
    view_data['post_tags'] = post_tags(filter={'user_id':view_data['post']['user_id']})

    view_data['title'] = "{}-{}".format(view_data['post']['title'], config['title'].TITLE)
    view_data['post_url'] = "{}{}".format(config['post'].DOMAIN, url_for('post.show', post_id=post_id))
    view_data['dest'] = ""
    for tag in view_data["post"]["tag"]:
        view_data['dest'] = "{},{}".format(view_data['dest'], tag)

    if "redirect" in view_data:
        return  redirect(view_data['redirect'])
    ua_key = 'noobw_ua'
    if ua_key in request.cookies:
        ua_id = request.cookies.get(ua_key)
        r = p_post_pv_1(post_id, ua_id)
        if r:
            view_data['post']['pv'] += 1
    else:
        r = p_post_pv_1(post_id, 0)
        if r:
            view_data['post']['pv'] += 1
        resp = make_response(render_template('post/show/post.html',  view_data=view_data))
        resp.set_cookie('noobw_ua', uuid(), config['cookie'].POST_TIMEOUT)
        return resp

    return render_template('post/show/post.html',  view_data=view_data)


# *******************************************************************************************************************
def cumulative_reply(comment, reply_id):

    '''

    累加评论

    '''

    r_c = mdb_cont.db.post_comment.find_one({'_id':ObjectId(reply_id), 'status':1})
    if r_c:

        if r_c['user_id']:
            comment = "{} //<a href='/people/{}' style='color:#1ab667;' >@{}</a>{}".format(
                                                                comment,
                                                                r_c['user_id'],
                                                                r_c['username'],
                                                                r_c['comment'],
                                                       )

        else:
            # 游客
            comment = "{} //<a style='color:#1ab667;' >@{}[游客]</a>{}".format(
                                                                comment,
                                                                r_c['user_id'],
                                                                r_c['username'],
                                                                r_c['comment'],
                                                       )

        if r_c['reply_id']:

            comment = cumulative_reply(comment, r_c['reply_id'])
    return comment

# *****************************************************************************************************************
@post.route('/preview/<post_id>', methods=['GET', 'POST'])
@login_required
def preview(post_id):

    view_data = {}
    # post
    view_data['post'] = mdb_cont.db.posts.find_one_or_404({'_id':ObjectId(post_id),'status':{'$ne':4}})
    if (current_user.id != view_data['post']['user_id'] or view_data['post']['status']==4 )and not current_user.can(Permission.AUDITOR) :
        abort(404)

    view_data['profile'] = mdb_user.db.user_profile.find_one_or_404({'user_id':view_data['post']['user_id']})
    view_data['username'] = mdb_user.db.user.find({"_id":view_data['post']['user_id']})["username"]
    view_data['title'] = "预览|{}-".format(view_data['post']['title'])
    return render_template('post/show/preview.html',  view_data=view_data)

# *****************************************************************************************************************
@post.route('/post-type', methods=['GET', 'POST'])
def post_type():

    type = request.args.get('type')
    tag = request.args.get('tag')

    view_data = get_post_type(type, tag)
    view_data['dest'] = "{}{}".format(type,tag)
    return render_template('post/show/posts_type.html',  view_data=view_data)

def get_post_type(type, tag):

    if type:
        filter = {'status':1, 'type':type}
    elif tag:
        filter = {'status':1, 'tag':tag}

    # 推荐post
    sort_f = [('praise',-1),('pv',-1)]
    view_data = p_posts(request, filter=filter)
    view_data['recommend'] = list(recommend_posts(sort=sort_f, filter=filter))

    # 类型
    view_data['post_types'] = post_types()
    # 标签
    view_data['post_tags'] = post_tags()
    #
    view_data['type'] = type
    view_data['tag'] = tag
    if type:
        view_data['title'] = '{}-{}'.format(type, config['title'].TITLE)
    else:
        view_data['title'] = '{}-{}'.format(tag, config['title'].TITLE)
    view_data['profile']={'user_id':'all'}

    return view_data


# ******************************************************************************************************
@post.route('/posts/subject', methods=['GET', 'POST'])
def posts_subject():

    sub = request.args.get('subject')

    #推荐post
    filter = {'status':1, 'subject':sub, "pv":{"$gte":config['post'].NEW_PV}}
    sort_f = [('praise',-1),('pv',-1)]
    view_data = p_posts(request, filter=filter)
    view_data['recommend'] = recommend_posts(sort=sort_f, filter=filter)

    # 标签
    view_data['post_tags'] = post_tags()
    #type
    view_data['subject'] = sub 
    if sub == "tech":
        view_data['name'] = "科技有趣"
    elif sub == "art":
        view_data['name'] = "音悦 | 文艺"

    view_data['title'] = '{}-{}'.format(view_data['name'],config['title'].TITLE)
    view_data['profile']={'user_id':'all'}

    return render_template('post/show/posts_subject.html',  view_data=view_data)


@post.route('/agreement', methods=['GET', 'POST'])
def sys_agr_show():

    type = request.args.get('type')
    t = request.args.get('t')
    # post
    filter={'subject':'sys', 'status':1}
    filter['title'] = t
    filter['type'] = type
    view_data  = p_post(filter=filter)
    if "redirect" in view_data:
        abort(404)

    if not current_user.is_anonymous():
        if current_user.id in view_data['post']['praise_id']:
            view_data['praise_status'] = True
    view_data['title'] = "{}-{}".format(view_data['post']['title'],config['title'].TITLE)
    # 推荐
    filter = {'status':1, 'type':'协议政策', 'subject':'sys'}
    view_data['recommend'] = recommend_posts(filter=filter)

    return render_template('post/show/sys_agr.html',  view_data=view_data)
