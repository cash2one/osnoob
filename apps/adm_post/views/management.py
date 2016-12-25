#-*-coding:utf-8-*-
import time
from apps import  mdb_cont
from apps.blueprint import admin
from apps.config import config, Permission, Theme
from apps.online.process.user import post_cnt_update
from apps.adm_post.forms.management import  SelectForm, DeleteForm, SearchForm
from bson import ObjectId
from flask import request, render_template, flash, url_for
from flask_login import login_required, current_user
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from bs4 import BeautifulSoup
from apps.shared_tools.decorator.decorators import permission_required
from apps.shared_tools.image.image_up import img_del
from apps.shared_tools.mdb_operation.paging import mongo_paging_post

__author__ = 'woo'

# 文章管理
@admin.route('/posts-management', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.AUDITOR)
def posts_management():
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

    view_data = {'page_name':'文章管理', 'title':'文章管理'}
    form = SearchForm()
    form_s = SelectForm()
    form_del = DeleteForm()
    #
    search_value = request.args.get('search_value')
    q = form_s.q.data = request.args.get('q','unqualified')
    view_data['state'] = q
    page_num = int(request.args.get('page',1))

    filter = {}
    if search_value:
        filter = {'title':{'$regex':search_value, "$options": 'i'}}

    if q == "audit":
        filter['status'] = 2

    elif q == "auto_audit":
        filter['status'] = 5

    elif q == "draft":
        filter['status'] = 0
    elif q == "been":
        filter['status'] = 1

    elif q == "unqualified":
        filter['status'] = 3

    elif q == "deleted":
        filter['status'] = 4
    elif q == "all":
        pass
    else:
        filter['status'] = 2

    # posts
    r = mongo_paging_post(mdb_cont.db.posts, filter, pre=config['paging'].POST_PER_PAGE,
                      page_num=page_num, sort=[('time',-1)], field={'body':0},is_paging=True)

    view_data['posts'] = r['datas']
    if not r['datas']:
        if page_num != 1:
            abort(404)
        view_data['msg'] = u'还没有任何东南西哦^_^'

    # nav
    view_data['l_page'] = r['l_page']
    view_data['n_page'] = r['n_page']
    view_data['l_show_num'] = r['l_show_num']
    view_data['n_show_num'] = r['n_show_num']
    view_data['page_num'] =  page_num
    view_data['page_cnt'] =  r['page_cnt']

    #
    now_time = time.time()
    now_time_0 = now_time - now_time%86400
    now_time_7 = now_time - 86400*6
    now_time_30 = now_time - 86400*29
    view_data['post_count'] =  mdb_cont.db.posts.find({"$or":[{'status':1},{'status':2},{'status':5}]}).count()
    view_data['post_count_d'] =  mdb_cont.db.posts.find({"$or":[{'status':1},{'status':2},{'status':5}],'$and':[{'time':{"$gte":now_time_0}}, {'time':{"$lt":now_time}}]}).count()
    view_data['post_count_7d'] =  mdb_cont.db.posts.find({"$or":[{'status':1},{'status':2},{'status':5}],'$and':[{'time':{"$gte":now_time_7}}, {'time':{"$lt":now_time}}]}).count()
    view_data['post_count_30d'] =  mdb_cont.db.posts.find({"$or":[{'status':1},{'status':2},{'status':5}],'$and':[{'time':{"$gte":now_time_30}}, {'time':{"$lt":now_time}}]}).count()
    return render_template('{}/post/posts.html'.format(Theme.ADM_THEME_NAME),
                           form= form ,
                           form_s=form_s,
                           form_del = form_del,
                           view_data=view_data)

# *********************************************************************************************************************
# 文章删除，恢复
@admin.route('/posts/op', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.AUDITOR)
def delete_post():

    form_del = DeleteForm()
    if form_del.validate_on_submit():
        id_list = request.form.getlist("boolean")
        id_len = len(id_list)
        op_type = form_del.op_type.data
        r = {'n':1}
        if op_type=='pass':
            for id in id_list:
                if id == 'y':
                    id_len -= 1
                    continue

                r=mdb_cont.db.posts.update({'_id':ObjectId(id), "$and":[{'status':{'$ne':4}},{'status':{'$ne':0}}]},
                                       {'$set':{'status':1}})

                if not r['n']:
                    flash({'msg':'非法:用户草稿和已移除文章不能审核'.format(id_len), 'type':'e'})
                    break
            post_cnt_update(mdb_cont.db.posts.find_one({'_id':ObjectId(id)})['user_id'])

            if r['n']:
                flash({'msg':'{}篇文章审核通过.'.format(id_len), 'type':'s'})

        elif op_type=='no_pass':
            for id in id_list:
                if id == 'y':
                    id_len -= 1
                    continue
                mdb_cont.db.posts.update({'_id':ObjectId(id)}, {'$set':{'status':3}})
            post_cnt_update(mdb_cont.db.posts.find_one({'_id':ObjectId(id)})['user_id'])
            flash({'msg':'{}篇文章审核未通过.'.format(id_len), 'type':'s'})

        elif op_type=='delete':
            for id in id_list:
                if id == 'y':
                    id_len -= 1
                    continue
                r = mdb_cont.db.posts.update({'_id':ObjectId(id), "$and":[{'status':{'$ne':4}},{'status':{'$ne':0}}]},
                                        {'$set':{'status':4}})
                if not r['n']:
                    flash({'msg':'非法:用户草稿和已移除文章不能移除'.format(id_len), 'type':'e'})
                    break
            post_cnt_update(mdb_cont.db.posts.find_one({'_id':ObjectId(id)})['user_id'])

            if r['n']:
                flash({'msg':'{}篇文章已移除到回收站.'.format(id_len), 'type':'s'})

        elif op_type=='recover':
            for id in id_list:
                if id == 'y':
                    id_len -= 1
                    continue
                r = mdb_cont.db.posts.update({'_id':ObjectId(id), 'status':4}, {'$set':{'status':2}})
                if not r['n']:
                    flash({'msg':'非法:已移除的才能恢复'.format(id_len), 'type':'e'})
                    break
            post_cnt_update(mdb_cont.db.posts.find_one({'_id':ObjectId(id)})['user_id'])

            if r['n']:
                flash({'msg':'{}篇文章已恢复.'.format(id_len), 'type':'s'})

        elif op_type=='delete_rec':
            if not current_user.can(Permission.ADMINISTER):
                flash({'msg':'非管理员无权永久删除.'.format(id_len), 'type':'w'})
            else:
                for id in id_list:
                    if id == 'y':
                        id_len -= 1
                        continue

                    post =  mdb_cont.db.posts.find_one_or_404({'_id':ObjectId(id), 'status':4})
                    img_url = post['img_url']

                    # 删除文章中的图片
                    del_post_imgs(post['body'])
                    r = mdb_cont.db.posts.remove({'_id':ObjectId(id), 'status':4})
                    if not r['n']:
                        flash({'msg':'非法:非回收站的不能永久删除.'.format(id_len), 'type':'e'})
                        break
                if r['n']:
                    flash({'msg':'{}篇文章已永久删除.'.format(id_len), 'type':'s'})
        else:
            abort(404)
        return redirect(url_for('admin.posts_management', q = form_del.q.data))
    else:
        abort(404)

# ---------------------------------------------------------------------------------------------------------------------
def del_post_imgs(str):
    soup = BeautifulSoup(str)
    imgs = soup.findAll("img")
    if imgs:
        for img in imgs:
            img_url = img['src']
            key = img_url.rsplit('/', 1)[-1]
            img_del({'bucket':config['upload'].IMG_B,'key':key})


