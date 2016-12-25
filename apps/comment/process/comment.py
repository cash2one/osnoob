#-*-coding:utf-8-*-
from random import randint
import time
from flask_mail import Message
from apps import mdb_user, config, cache, mdb_sys, mdb_cont
from apps.msg.process.msgs import add_msg
from bson.objectid import ObjectId
from flask import url_for, render_template
from flask_login import current_user
from apps.shared_tools.email.email_format import ver_email
from apps.shared_tools.email.send_email import send_email
from apps.shared_tools.mdb_operation.paging import mongo_paging_comment
from apps.shared_tools.region.osn_format import request_path


def p_comments(request, post_id, filter={"$or":[{'status':1},{'status':2},{'status':3},{'status':5}]},sort=[('time',-1)]):
    t_filter = filter.copy()
    t_filter['post-id'] = post_id
    request_path(t_filter)
    view_data = get_p_comments(request, post_id, filter, sort)
    return view_data

@cache.cached(timeout=config['cache_timeout'].POST)
def get_p_comments(request, post_id, filter={"$or":[{'status':1},{'status':2},{'status':3},{'status':5}]},sort=[('time',-1)]):

    view_data = {}
    page_num = int(request.args.get('page',1))
    r = mongo_paging_comment(mdb_cont.db.post_comment,
                             filter,
                             pre=config['paging'].POST_COMMENT,
                             page_num=page_num,
                             sort=sort)
    view_data['comment_cnt'] = mdb_cont.db.post_comment.find({'case_id':ObjectId(post_id), 'status':1}).count()
    #
    mdb_cont.db.posts.update({'_id':ObjectId(post_id)}, {'$set':{'comment_cnt':view_data['comment_cnt']}})
    #
    view_data['comments'] = []
    avatar_l = len(config['user'].AVATAR_URL)
    for c in r['datas']:
        avatar_url = config['user'].AVATAR_URL[randint(0,avatar_l-1)]
        if not c['user_id']:
            c['avatar_url'] = avatar_url
        else:
            c['avatar_url'] = mdb_user.db.user_profile.find_one({'user_id':c['user_id']})['avatar_url']

        if c['reply_id']:
            c['comment'] = cumulative_reply(c['comment'], c['reply_id'])
        c['_id'] = str(c['_id'])
        c['case_id'] = str(c['case_id'])
        c['reply_id'] = str(c['reply_id'])

        # lable , delete
        c['delete_s'] = 'hidden'
        if current_user.is_anonymous():
            if c['user_id']:
                c['lable_f'] = "label label-name-n bg-success m-l-xs"
                c['lable'] = '用户'
            else:
                c['lable_f'] = "label label-name-n bg-info m-l-xs"
                c['lable'] = '游客'
        else:
            if current_user.id == c['user_id']:
                c['lable_f'] = "label label-name-n bg-primary m-l-xs"
                c['lable'] = '我'
                c['delete_s'] = ''
            elif not c['user_id']:
                c['lable_f'] = "label label-name-n bg-info m-l-xs"
                c['lable'] = '游客'
            else:
                c['lable_f'] = "label label-name-n bg-success m-l-xs"
                c['lable'] = '用户'

        # audit
        c['audit'] = {'s3':'hidden', 's2':'hidden'}
        if c['status'] != 1:
            if not current_user.is_anonymous() and current_user.id == c['user_id']:
                if c['status'] == 3:
                    c['audit']['s3'] = ''
                else:
                    c['audit']['s2'] = ''
                view_data['comments'].append(c)
        else:
            view_data['comments'].append(c)
    view_data['n_page'] = r['n_page']
    return view_data



# ----------------------------------------------------------------------------------------------------------------------
# 累加回复评论
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
                                                                r_c['username'],
                                                                r_c['comment'],
                                                       )

        if r_c['reply_id']:

            comment = cumulative_reply(comment, r_c['reply_id'])
    return comment

# ----------------------------------------------------------------------------------------------------------------------
def p_add_comment(username, email, case_id, comment, reply_id=None):

    '''
    comment status
    1:通过
    2:待审核
    ３:未通过
    ４：已删除
    5:自动审核通过
    :return:
    '''

    view_data = {'flash':None}
    if reply_id and not current_user.is_authenticated():
        view_data['flash'] = {'msg':'<span>回复请<a style="color:#1AB667" href="{}">登录</a></span>'.format(url_for('online.login')), 'type':'html'}
    elif not current_user.is_authenticated() and (username.strip() == "" or username == None):
        view_data['flash'] = {'msg':u'游客必须填写名号', 'type':'w'}
    elif not current_user.is_authenticated() and (email.strip() == "" or email == None):
        view_data['flash'] = {'msg':u'游客必须填写邮箱,邮箱不会公布！', 'type':'w'}
    elif not current_user.is_authenticated() and not ver_email(email):
        view_data['flash'] = {'msg':u'邮箱格式不对哦！', 'type':'w'}

    elif not current_user.is_authenticated() and mdb_user.db.user.find_one({"username":username.strip()}):
        view_data['flash'] = {'msg':u'这名号已被使用', 'type':'w'}

    elif not current_user.is_authenticated() \
            and not mdb_cont.db.post_comment.find_one({'email':email.strip(),
                                              'username':username.strip(),
                                              'status':1,
                                              'case_id':case_id})\
            and mdb_cont.db.post_comment.find_one({'username':username.strip(),
                                              'status':1,
                                              'case_id':case_id}):
            view_data['flash'] = {'msg':u'这名号已被使用', 'type':'w'}

    elif not comment.strip():
        view_data['flash'] = {'msg':u'评论不能为空哦！', 'type':'w'}
    if not view_data['flash']:
        try:
            now_cnt = len(comment.strip().encode("gbk").decode("gbk"))
            if now_cnt > config['comment'].COMMENT_MAX:
                c_cnt = now_cnt-300
                view_data['flash'] = {'msg':u'评论最多{}个字！已超{}个字'.format(config['comment'].COMMENT_MAX, c_cnt), 'type':'w'}
        except:
            view_data['flash'] = {'msg':u'评论系统错误,文字格式异常', 'type':'e'}

    if view_data['flash']:
        return view_data

    # ------------------------------------------------------------------------------------------------------------------
    if username.strip() == "" or username == None:
         # 用户是否评论频繁
        u_p = mdb_user.db.user_profile.find_one({'user_id':current_user.id})
        if 'last_comment' in u_p:
            last_comment = u_p['last_comment']
            if (time.time() - last_comment) < config['comment'].INTERVAL:
                view_data['flash'] = {'msg':u'评论太频繁！请间隔{}秒'.format(config['comment'].INTERVAL), 'type':'w'}
                return view_data
        username = current_user.username
        user_id = current_user.id
        email = None
    else:
        username = username.strip()
        user_id = None
        email = email.strip()

    # 如果是登录用户　&　有n次评论审核通过
    if current_user.is_authenticated():
        status = 1
        case_status = 1
        #　记录最后一次评论时间
        mdb_user.db.user_profile.update({'user_id':current_user.id},{'$set':{'last_comment':time.time()}})
    else:
        status = 1
        case_status = 1
    if reply_id:
        reply_id = ObjectId(reply_id)

    co = {
            'username':username,
            'email':email,
            'case_id':ObjectId(case_id),
            'user_id':user_id,
            'comment':comment,
            'time':time.time(),
            'reply_id':reply_id,
            'praise':0,
            'status':status,
        }
    _id = mdb_cont.db.post_comment.insert(co)
    # 消息记录
    if not reply_id:
        # 给post用户
        post = mdb_cont.db.posts.find_one({'_id':ObjectId(case_id)})
        if post:
            case_user_id = post['user_id']
            if case_user_id and  current_user.is_anonymous():
                add_msg('{}: 评论'.format(username),
                            url="{}#{}".format(url_for('post.show', post_id=case_id), str(_id)),
                            user_id=case_user_id,
                            case_id=ObjectId(_id),
                            case_status = case_status,
                            sub='post',
                            type='new_comment')
            else:
                if case_user_id and post['user_id'] != current_user.id:
                    add_msg('{}: 评论'.format(username),
                            url="{}#{}".format(url_for('post.show', post_id=case_id), str(_id)),
                            user_id=case_user_id,
                            case_id=ObjectId(_id),
                            case_status = case_status,
                            sub='post',
                            type='new_comment')
    else:
        # 给comment用户
        c = mdb_cont.db.post_comment.find_one({'_id':ObjectId(reply_id)})
        if c:
            case_user_id = c['user_id']
            if case_user_id and c['user_id'] != current_user.id:
                add_msg('{}: 评论回复'.format(username),
                        url="{}#{}".format(url_for('post.show', post_id=case_id), str(_id)),
                        user_id=case_user_id,
                        case_id=ObjectId(_id),
                        case_status = case_status,
                        sub='post',
                        type='reply_comment')
            else:

                view_data = {"post_name":"",
                             "username":c["username"],
                             "url":"{}{}#{}".format(config['post'].DOMAIN, url_for('post.show', post_id=case_id), str(_id))}
                print view_data
                html = render_template('online/email/comment_reply.html', view_data=view_data)
                # send email
                msg = Message("您在菜鸟世界官网的评论有人回复啦!".format(config['email'].MAIL_PROJECT),
                sender=config['email'].MAIL_DEFAULT_SENDER,
                recipients=[c["email"]])
                msg.html = html
                send_email(mdb_sys.db, msg)


    co['_id'] = str(_id)
    co['case_id'] = str(co['case_id'])
    co['reply_id'] = str(co['reply_id'])
    if current_user.is_anonymous():
        co['anonymous'] = True
    return co


# ----------------------------------------------------------------------------------------------------------------------
def p_del_comment(cid, user_id):

    is_self_admin(user_id)
    r = mdb_cont.db.post_comment.update({'_id':ObjectId(cid), 'user_id':user_id},{'$set':{'status':4}})

    return r