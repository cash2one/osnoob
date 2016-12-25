#-*-coding:utf-8-*-
import time
from apps import mdb_cont, mdb_sys
from apps.config import config, Permission, Theme
from apps.online.process.user import post_cnt_update
from apps.post.forms.posts import EditPost
from apps.blueprint import post
from apps.post.process.post import post_img_statis, edit_img_log_claer, post_img, sys_edit_img_log_claer
from bson import ObjectId
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.exceptions import abort

__author__ = 'woo'

@post.route('/add', methods=['GET', 'POST'])
@login_required
def post_add():

    '''
    status:
    0:草稿
    １:发布
    ２：待审核
    ３：审核未通过
    ４：已删除
    ５：自动审核通过
    :return:
    '''

    view_data = {'title':u'发表-{}'.format(config['title'].TITLE), 'hint':'写点东西'}
    view_data['permission'] = Permission.ECP
    view_data['help'] = mdb_cont.db.posts.find_one({'type':u'帮助', 'title':u'文章编辑帮助'})
    subject = request.args.get('subject')
    if subject=="tech":
        view_data['hint'] = '科技有趣'
    elif subject=="ART":
        view_data['hint'] = '音乐｜艺术'
    elif subject=="sys":
        if not current_user.can(Permission.ADMINISTER) and not current_user.is_role(Permission.ECP):
            abort(404)
        view_data['hint'] = '系统告示'

    if not subject in config['post'].SUBJECT:
        abort(404)
    else:
        form = EditPost(subject)

    if form.issue.data:
        if not form.title.data:
            flash({'type':'w','msg':u'标题不能为空哦！'})
            form.s_type.data = form.s_type.data
            form.body.data = form.body.data
            return render_template('post/posts/edit.html', form=form, view_data=view_data)

        # if current_user.can(Permission.ECP):
        #     status = 1
        # else:
        #     status = 2
        status = 1
        # 封面图片
        img_url = post_img(form.body.data,form.s_type.data)
        form.body.data = edit_img_log_claer(form.body.data, None)
        tag_list = request.form.getlist("boolean_l")
        post = {
            'user_id':current_user.id,
            'title':form.title.data.strip(),
            'body':form.body.data,
            'tag':tag_list,
            'type':form.s_type.data,
            'img_url':img_url,
            'praise':0,
            'praise_id':[],
            'pv':0,
            'pv_id':[],
            'status':status,
            'time':time.time(),
            'update_time':time.time(),
            'is_been':1,
            'subject':subject,
        }
        post_id = mdb_cont.db.posts.insert(post)
        post_cnt_update(current_user.id)
        if status == 1:
            flash({'msg':u'发表成功!首页|专栏可能延迟{}秒推出.'.format(config['cache_timeout'].POSTS), "type":'s'})
            return redirect(url_for('post.show', post_id=post_id))
        else:
            return redirect(url_for('post.preview', post_id=post_id))

    elif form.draft.data:
        if not form.title.data:
            flash({'type':'w','msg':u'标题不能为空哦！'})
            form.s_type.data = form.s_type.data
            form.body.data = form.body.data
            return render_template('post/posts/edit.html', form=form, view_data=view_data)
        tag_list = request.form.getlist("boolean_l")

        # 封面图片
        img_url = post_img(form.body.data, form.s_type.data)
        form.body.data = edit_img_log_claer(form.body.data, None)
        post = {
            'user_id':current_user.id,
            'title':form.title.data.strip(),
            'body':form.body.data,
            'tag':tag_list,
            'type':form.s_type.data,
            'img_url':img_url,
            'praise':0,
            'praise_id':[],
            'pv':0,
            'pv_id':[],
            'status':0,
            'time':time.time(),
            'update_time':time.time(),
            'is_been':0,
            'subject':subject,
        }
        post_id = mdb_cont.db.posts.insert(post)
        post_cnt_update(current_user.id, )
        return redirect(url_for('post.preview', post_id=post_id))

    # view_data
    view_data['tag_s'] = []
    tags = mdb_sys.db.type.find_one({'project':"post-tag", "subject":"tag"})
    if tags:
        view_data['tag_s'] = tags["type"]

    view_data['tag_u'] = []
    tags = mdb_cont.db.tag.find_one({'user_id':ObjectId(current_user.id)})
    if tags:
        view_data['tag_u'] = tags['tag']

    view_data['post'] = {'img_url':'images/post_img/未分类_default.png'}
    return render_template('{}/post/edit.html'.format(Theme.THEME_NAME), form=form, view_data=view_data)


# *********************************************************************************************************************
@post.route('/<post_id>/edit', methods=['GET', 'POST'])
@login_required
def post_edit(post_id):

    view_data = {'title':u'编辑-{}'.format(config['title'].TITLE), 'hint':'正在编辑'}
    view_data['permission'] = Permission.ECP
    view_data['help'] = mdb_cont.db.posts.find_one({'type':u'帮助', 'title':u'文章编辑帮助'})
    post = mdb_cont.db.posts.find_one_or_404({'_id':ObjectId(post_id), 'user_id':current_user.id})
    if post['subject']=="tech":
        view_data['hint'] = '科技有趣'
    elif post['subject']=="art":
        view_data['hint'] = '音乐｜艺术'
    elif post['subject']=="sys":
        if not current_user.is_role(Permission.ECP):
            abort(404)
        view_data['hint'] = '系统告示'

    form = EditPost(post['subject'])
    if form.issue.data:
        # if current_user.can(Permission.ECP):
        #     status = 1
        # else:
        #     status = 2
        status = 1
        tag_list = request.form.getlist("boolean_l")
        # 封面图片
        img_url = post_img(form.body.data, form.s_type.data)
        if current_user.username == u"菜鸟世界":
            form.body.data =  sys_edit_img_log_claer(form.body.data, post_title=form.title.data.strip())
        else:
            form.body.data = edit_img_log_claer(form.body.data, post_id)
        # tag
        if post['is_been']:
            _time = post['time']
            _is_been = post['is_been']
        else:
            _time = time.time()
            _is_been = 1
        post = {
                'title':form.title.data.strip(),
                'body':form.body.data,
                'status':status,
                'type':form.s_type.data,
                'img_url':img_url,
                'time':_time,
                'is_been':_is_been,
                'update_time':time.time(),
            }
        if tag_list:
            post['tag'] = tag_list

        mdb_cont.db.posts.update({'_id':ObjectId(post_id), 'user_id':current_user.id}, {'$set':post})
        if status == 1:
            post_cnt_update(current_user.id)
            flash({'msg':u'更新成功!首页|专栏可能延迟{}秒更新.'.format(config['cache_timeout'].POSTS), "type":'s'})
            return redirect(url_for('post.show', post_id=post_id))
        else:
            return redirect(url_for('post.preview', post_id=post_id))

    elif form.draft.data:
        status = 0
        tag_list = request.form.getlist("boolean_l")
       # 图片
        img_url = post_img(form.body.data, form.s_type.data)
        form.body.data = edit_img_log_claer(form.body.data, post_id)

        post = {
            'title':form.title.data.strip(),
            'body':form.body.data,
            'type':form.s_type.data,
            'img_url':img_url,
            'status':status,
            'update_time':time.time()
        }
        if tag_list:
            post['tag'] = tag_list
        post_cnt_update(current_user.id)
        mdb_cont.db.posts.update({'_id':ObjectId(post_id), 'user_id':current_user.id}, {'$set':post})
        return redirect(url_for('post.preview', post_id=post_id))

    # view_data

    view_data['tag_s'] = []
    tags = mdb_cont.db.tag.find_one({'user_id':0})
    if tags:
        view_data['tag_s'] = tags['tag']

    view_data['tag_u'] = []
    tags = mdb_cont.db.tag.find_one({'user_id':current_user.id})
    if tags:
        view_data['tag_u'] = tags['tag']

    #post

    form.title.data = post['title']
    form.body.data = post['body']
    form.s_type.data = post['type']
    view_data['edit'] = True
    view_data['post'] = post
    # 记录图片url
    post_img_statis(post['body'], post['_id'])

    return render_template('post/posts/edit.html', form=form, view_data=view_data)

