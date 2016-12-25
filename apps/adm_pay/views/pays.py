#-*-coding:utf-8-*-
from apps import mdb_user
from apps.blueprint import pay
from apps.config import Permission, Theme
from apps.adm_pay.forms.pay import SearchForm, SelectForm, DeleteForm
from bson import ObjectId
from flask import request, render_template, flash, url_for
from flask_login import login_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from apps.shared_tools.decorator.decorators import permission_required
from apps.shared_tools.mdb_operation.paging import mongo_paging_user

__author__ = 'woo'

# *********************************************************************************************************************
# 文章管理
@pay.route('/pay-management', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.AUDITOR)
def pays_management():
    '''
    status:
    0:未审核
    １:通过
    ２：未通过
    :return:
    '''

    view_data = {'page_name':'支付二维码'}
    form = SearchForm()
    form_s = SelectForm()
    form_del = DeleteForm()
    #
    search_value = request.args.get('search_value')
    q = form_s.q.data = request.args.get('q','audit')
    view_data['state'] = q
    page_num = int(request.args.get('page',1))

    filter = {'pay':{'$exists':False}, 'pay':{'$ne':[]}}
    if search_value:
        filter['username'] = {'$regex':search_value}

    if q == "audit":
        filter['$or'] = [{'pay.alipay.status':0}, {'pay.wechatpay.status':0}]

    elif q == "unqualified":
        filter['$or'] = [{'pay.alipay.status':2}, {'pay.wechatpay.status':2}]
    elif q == "pass":
        filter['$or'] = [{'pay.alipay.status':1}, {'pay.wechatpay.status':1}]

    # posts
    r = mongo_paging_user(mdb_user.db.user_profile, filter, pre=6,
                      page_num=page_num, sort=[('time',-1)], field={'body':0})

    view_data['users'] = r['datas']
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
    return render_template('{}/pay/pays.html'.format(Theme.ADM_THEME_NAME),
                           form= form ,
                           form_s=form_s,
                           form_del = form_del,
                           view_data=view_data)


# *********************************************************************************************************************
# 文章删除，恢复
@pay.route('/op', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.AUDITOR)
def delete_pay():

    form_del = DeleteForm()
    if form_del.validate_on_submit():
        id_list = request.form.getlist("boolean")
        id_len = len(id_list)
        op_type = form_del.op_type.data
        r = {'n':1}
        if op_type=='pass':
            for id in id_list:
                if id[0] == 'y':
                    id_len -= 1
                    continue
                id =  id.replace('ObjectId(','u').replace(')','')
                id = eval(id)
                t_set = 'pay.{}.status'.format(id[1])
                r=mdb_user.db.user_profile.update({'_id':ObjectId(id[0])}, {'$set':{t_set:1}})
                if not r['n']:
                    flash({'msg':'操作失败'.format(id_len), 'type':'w'})
                    break
            if r['n']:
                flash({'msg':'{}支付码审核通过.'.format(id_len), 'type':'s'})

        elif op_type=='no_pass':
            for id in id_list:
                if id[0] == 'y':
                    id_len -= 1
                    continue
                id =  id.replace('ObjectId(','u').replace(')','')
                id = eval(id)
                t_set = 'pay.{}.status'.format(id[1])
                mdb_user.db.user_profile.update({'_id':ObjectId(id[0])}, {'$set':{t_set:2}})

            flash({'msg':'{}支付码审核未通过.'.format(id_len), 'type':'s'})
        else:
            abort(404)
        return redirect(url_for('pay.pays_management', q = form_del.q.data))
    else:
        abort(404)