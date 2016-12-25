# -*-coding:utf-8-*-
from datetime import datetime
from apps import mdb_user, mdb_cont
from apps.adm_user.models.user import User, Permission
from apps.config import config
from apps.blueprint import comments
from apps.comment.forms.comment import CommentForm
from bson import ObjectId
from flask import request, flash, url_for
from flask_login import login_required, current_user
import re
from werkzeug.utils import redirect


@comments.route('/', methods=['GET', 'POST'])
def comment_add():
    '''
    comment status
    1:通过
    2:待审核
    ３:未通过
    ４：已删除
    5:自动审核通过
    :return:
    '''
    form = CommentForm()
    positioning = "#comment"
    if form.submit.data:

        if not current_user.is_authenticated() and (form.username.data.strip() == "" or form.username.data == None):
            flash({'msg':u'游客必须填写名号', 'type':'w'})
        elif not current_user.is_authenticated() and (form.email.data.strip() == "" or form.email.data == None):
            flash({'msg':u'游客必须填写邮箱,邮箱不会公布！', 'type':'w'})

        elif not current_user.is_authenticated() and not re.search(r"^[a-z]([a-z0-9]*[-_]?[a-z0-9]+)*@([a-z0-9]*[-_]?[a-z0-9]+)+[\.][a-z]+$",
                       form.email.data.strip()):
            flash({'msg':u'邮箱格式不对哦！', 'type':'w'})

        elif User.query.filter_by(username=form.username.data.strip()).first():

            flash({'msg':u'这名号已被使用', 'type':'w'})


        elif not current_user.is_authenticated() \
                and not mdb_cont.db.post_comment.find_one({'email':form.email.data.strip(),
                                                  'username':form.username.data.strip(),
                                                  'status':1,
                                                  'case_id':form.case_id.data})\
                and mdb_cont.db.post_comment.find_one({'username':form.username.data.strip(),
                                                  'status':1,
                                                  'case_id':form.case_id.data}):
                flash({'msg':u'这名号已被使用', 'type':'w'})

        elif not form.comment.data.strip():
            flash({'msg':u'评论不能为空哦！', 'type':'w'})

        elif len(form.comment.data.strip().encode("gbk").decode("gbk")) > config['comment'].COMMENT_MAX:

            form.comment.data = form.comment.data
            flash({'msg':u'评论不能大于{}个字！'.format(config['comment'].COMMENT_MAX), 'type':'w'})

        else:
            positioning = "#comment-top"
            if form.username.data.strip() == "" or form.username.data == None:
                username = current_user.username
                user_id = current_user.id
                email = None
            else:
                username = form.username.data.strip()
                user_id = None
                email = form.email.data.strip()

            # 如果是登录用户　&　有n次评论审核通过
            if current_user.is_authenticated() and mdb_cont.db.post_comment.find({'user_id':current_user.id, 'status':1}).count() >= config['comment'].PASS_CNT:
                status = 1
            elif current_user.can(Permission.AUDITOR):
                status = 1
            else:
                status = 2
            if form.reply_id.data:
                form.reply_id.data = ObjectId(form.reply_id.data)
            co = {
                'username':username,
                'email':email,
                'case_id':ObjectId(form.case_id.data),
                'user_id':user_id,
                'comment':form.comment.data,
                'time':datetime.now(),
                'reply_id':form.reply_id.data,
                'praise':0,
                'status':status,
            }
            mdb_cont.db.post_comment.insert(co)

    elif form.praise_btn.data:
        _post = mdb_cont.db.posts.find_one({'_id':ObjectId(form.case_id.data)},{'praise':1,'praise_id':1})
        if not current_user.is_authenticated() and request.remote_addr in _post['praise_id']:
            flash({'msg':u'同一IP不能重复点赞哦！','type':'w'})

        elif current_user.is_authenticated() and current_user.id in _post['praise_id']:
            flash({'msg':u'同个用户只能赞一次哦！','type':'w'})

        else :
            if current_user.is_authenticated():
                praise_id = current_user.id
            else:
                praise_id = request.remote_addr
            praise = _post['praise'] + 1
            _post['praise_id'].append(praise_id)
            mdb_cont.db.posts.update({'_id':ObjectId(form.case_id.data)}, {'$set':{'praise':praise,
                                                                              'praise_id':_post['praise_id'],
                                                                              }})

        return redirect(url_for('post.show', post_id=form.case_id.data))

    return redirect("{}{}".format(url_for('post.show', post_id=form.case_id.data), positioning))