#-*-coding:utf-8-*-
import time
from apps import  mdb_cont
from apps.adm_comment.forms.comment import CommentSelectForm, SearchForm, DeleteForm
from apps.blueprint import admin
from apps.config import config, Permission, Theme
from bson import ObjectId
from flask import request, render_template, flash, url_for
from flask_login import login_required, current_user
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from apps.shared_tools.decorator.decorators import permission_required
from apps.shared_tools.mdb_operation.paging import mongo_paging_post

# 评论管理
@admin.route('/comments-management', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.AUDITOR)
def comments_management():
    '''
    comment status
    1:通过
    2:待审核
    ３:未通过
    ４：已删除
    5:自动审核通过
    :return:
    '''

    view_data = {'page_name':'评论管理', 'title':'评论管理'}
    form = SearchForm()
    form_s = CommentSelectForm()
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
    r = mongo_paging_post(mdb_cont.db.post_comment, filter, pre=config['paging'].POST_PER_PAGE,
                      page_num=page_num, sort=[('time',-1)],is_paging=True)

    view_data['comments'] = r['datas']
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
    view_data['c_count'] =  mdb_cont.db.post_comment.find({"$or":[{'status':1},{'status':2},{'status':5}]}).count()
    view_data['c_count_d'] =  mdb_cont.db.post_comment.find({"$or":[{'status':1},{'status':2},{'status':5}],'$and':[{'time':{"$gte":now_time_0}}, {'time':{"$lt":now_time}}]}).count()
    view_data['c_count_7d'] =  mdb_cont.db.post_comment.find({"$or":[{'status':1},{'status':2},{'status':5}],'$and':[{'time':{"$gte":now_time_7}}, {'time':{"$lt":now_time}}]}).count()
    view_data['c_count_30d'] =  mdb_cont.db.post_comment.find({"$or":[{'status':1},{'status':2},{'status':5}],'$and':[{'time':{"$gte":now_time_30}}, {'time':{"$lt":now_time}}]}).count()
    return render_template('{}/post/comments.html'.format(Theme.ADM_THEME_NAME),
                           form= form ,
                           form_s=form_s,
                           form_del = form_del,
                           view_data=view_data)

# 评论删除，恢复
@admin.route('/comments/op', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.AUDITOR)
def delete_comment():
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

                r=mdb_cont.db.post_comment.update({'_id':ObjectId(id), "$and":[{'status':{'$ne':4}},{'status':{'$ne':0}}]},
                                       {'$set':{'status':1}})
                if not r['n']:
                    flash({'msg':'非法:已移除评论不能审核'.format(id_len), 'type':'e'})
                    break
                mdb_user.db.msg.update({'case_id':ObjectId(id), 'sub':'post'}, {'$set':{'case_status':1}})
            if r['n']:
                flash({'msg':'{}条评论审核通过.'.format(id_len), 'type':'s'})

        elif op_type=='no_pass':
            for id in id_list:
                if id == 'y':
                    id_len -= 1
                    continue
                mdb_cont.db.post_comment.update({'_id':ObjectId(id)}, {'$set':{'status':3}})

            flash({'msg':'{}条评论审核未通过.'.format(id_len), 'type':'s'})

        elif op_type=='delete':
            for id in id_list:
                if id == 'y':
                    id_len -= 1
                    continue
                r = mdb_cont.db.post_comment.update({'_id':ObjectId(id), "$and":[{'status':{'$ne':4}},{'status':{'$ne':0}}]},
                                        {'$set':{'status':4}})
                if not r['n']:
                    flash({'msg':'非法:已移除评论不能移除'.format(id_len), 'type':'e'})
                    break
            if r['n']:
                flash({'msg':'{}条评论已移除到回收站.'.format(id_len), 'type':'s'})

        elif op_type=='recover':
            for id in id_list:
                if id == 'y':
                    id_len -= 1
                    continue
                r = mdb_cont.db.post_comment.update({'_id':ObjectId(id), 'status':4}, {'$set':{'status':2}})
                if not r['n']:
                    flash({'msg':'非法:已移除的才能恢复'.format(id_len), 'type':'e'})
                    break
            if r['n']:
                flash({'msg':'{}条评论已恢复.'.format(id_len), 'type':'s'})

        elif op_type=='delete_rec':
            if not current_user.can(Permission.ADMINISTER):
                flash({'msg':''.format(id_len), 'type':'w'})
            else:
                for id in id_list:
                    if id == 'y':
                        id_len -= 1
                        continue
                    r = mdb_cont.db.post_comment.remove({'_id':ObjectId(id), 'status':4})
                    if not r['n']:
                        flash({'msg':'非法:非回收站的不能永久删除.'.format(id_len), 'type':'e'})
                        break
                if r['n']:
                    flash({'msg':'{}条评论已永久删除.'.format(id_len), 'type':'s'})
        else:
            abort(404)
        return redirect(url_for('admin.comments_management', q = form_del.q.data))
    else:
        abort(404)
