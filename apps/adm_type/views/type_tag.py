#-*-coding:utf-8-*-
from apps import mdb_sys
from apps.config import Permission, Theme
from apps.blueprint import admin
from apps.adm_type.forms.type_tag import PostTypeDelForm, AddPostTypeForm
from bson import ObjectId
from flask import render_template, request, flash, url_for
from flask_login import login_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from apps.shared_tools.decorator.decorators import permission_required

__author__ = 'woo'

# *********************************************************************************************************************
# 规则管理
@admin.route('/types', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def types():
    view_data = {'title':'类型标签', 'page_name':'类型标签'}
    form_del = PostTypeDelForm()
    view_data['types'] = []

    # type
    types = mdb_sys.db.type.find({'project':{'$exists':True}, "subject":{'$exists':True}, 'type':{'$exists':True}})
    for tp in types:

        if (type(tp['type'][0]) != type([]) and type(tp['type'][0]) != type({})) or not tp["type"]:
            temp_type = ""
            for t in tp['type']:
                temp_type = "{};{}".format(temp_type, t)
            temp_type = temp_type.strip(";")
        else:
            temp_type = tp['type']

        view_data['types'].append({'project':tp['project'],'subject':tp['subject'], 'type':temp_type, "_id":tp['_id']})
    # tag
    # _post_tag = mdb_cont.db.tag.find_one_or_404({'user_id':0})
    # view_data['types'].append({'name':'tag', 'values':_post_tag['tag'], "_id":_post_tag['_id']})
    return render_template('{}/type/types.html'.format(Theme.ADM_THEME_NAME), view_data=view_data, form_del=form_del)

# *********************************************************************************************************************
# 规则编辑
@admin.route('/type/add', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def type_add():
    view_data = {'title':'POST类型添加', 'page_name':'POST类型添加'}
    form = AddPostTypeForm()

    if form.submit.data:
        if form.value.data.strip()[0] == "{" and form.value.data.strip()[-1] == "}":
            try:
                type_list = eval(form.value.data.strip())
            except:
                flash({'type':'e', 'msg':'格式错误，需要一个json {}'})
        elif form.value.data.strip()[0] == "[" and form.value.data.strip()[-1] == "]":
            try:
                type_list = eval(form.value.data.strip())
            except:
                flash({'type':'e', 'msg':'格式错误，需要一个数组[]'})

        else:
            temp = form.value.data.strip().replace("；", ";")
            type_list= temp.strip(';').split(";")
        t = {
            'project':form.project.data.strip(),
            'subject':form.subject.data.strip(),
            'type':type_list,
        }
        mdb_sys.db.type.insert(t)
        return redirect(url_for('admin.types'))
    return render_template('{}/type/type_add.html'.format(Theme.ADM_THEME_NAME), view_data=view_data, form=form)


# *********************************************************************************************************************
# 规则编辑
@admin.route('/type/edit/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def type_edit(id):
    view_data = {'title':'POST类型编辑', 'page_name':'POST类型编辑'}
    form = AddPostTypeForm()

    if form.submit.data:
        if form.value.data.strip()[0] == "{" and form.value.data.strip()[-1] == "}":
            try:
                type_list = eval(form.value.data.strip())
            except:
                flash({'type':'e', 'msg':'格式错误，需要一个json {}'})
        elif form.value.data.strip()[0] == "[" and form.value.data.strip()[-1] == "]":
            try:
                type_list = eval(form.value.data.strip())
            except:
                flash({'type':'e', 'msg':'格式错误，需要一个数组[]'})
        else:
            temp = form.value.data.strip().replace("；", ";")
            type_list= temp.strip(';').split(";")
        t = {
            "project":form.project.data,
            "subject":form.subject.data,
            'type':type_list,
        }
        mdb_sys.db.type.update({"_id":ObjectId(id)},{"$set":t})
        return redirect(url_for('admin.types'))

    type_t = mdb_sys.db.type.find_one_or_404({"_id":ObjectId(id)})
    form.project.data = type_t["project"]
    form.subject.data = type_t["subject"]
    view_data["subject"] =type_t["subject"]
    if not type_t["type"] or (type(type_t['type'][0]) != type([]) and type(type_t['type'][0]) != type({})):
        temp_type = ""
        for t in type_t['type']:
            temp_type = "{};{}".format(temp_type, t)
        temp_type = temp_type.strip(";")
        form.value.data = temp_type
    else:
        form.value.data = type_t['type']
    return render_template('{}/type/type_edit.html'.format(Theme.ADM_THEME_NAME), view_data=view_data, form=form)

# *********************************************************************************************************************
# 规则删除
@admin.route('/post/type/delete', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def delete_type():

    form_del = PostTypeDelForm()
    if form_del.submit.data:
        id_list = request.form.getlist("boolean")
        id_len = len(id_list)
        op_type = form_del.op_type.data
        if op_type=='delete':
            for id in id_list:
                if id == 'y':
                    id_len -= 1
                    continue
                mdb_sys.db.type.remove({'_id':ObjectId(id)})
            flash({'msg':u'删除了{}种类型'.format(id_len), 'type':'s'})

        return redirect(url_for('admin.types'))
    abort(404)



