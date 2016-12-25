#-*-coding:utf-8-*-
import time
from random import randint
from bson import ObjectId
from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import current_user, login_required
from apps import mdb_user, config, mdb_cont, mdb_sys
from apps.blueprint import admin
from apps.adm_user.forms.user import  EditProfileAdminForm, RoleForm, DeleteForm, AddUserForm, SelectForm
from apps.adm_user.forms.user import SearchForm
from apps.adm_user.forms.user import PasswordResetAdmin
from apps.config import Permission, Theme
from apps.online.process.user_verify import User
from apps.shared_tools.decorator.decorators import permission_required
from apps.shared_tools.mdb_operation.paging import mongo_paging
from apps.user.models.user import user_model

__author__ = 'woo'
'''
USER VIEWS
'''

# *********************************************************************************************************************
@admin.route('/add-user', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def add_user():

    view_data = {'title':'添加用户'}
    form = AddUserForm()
    if form.validate_on_submit():
        user = user_model(username=form.username.data,
                          email=form.email.data,
                          password=form.password.data,
                          domain=-1,
                          role_id=form.role.data,
                          active=True)

        r = mdb_user.db.role.find_one({"_id":ObjectId(form.role.data)})["permissions"] >= Permission.ROOT
        if  r and not current_user.auth_judge(Permission.ROOT):
            flash({'msg':'你没有权限添加超级管理员','type':'w'})
            return render_template('admin/user/add_user.html', form=form)

        names = mdb_sys.db.audit_rules.find_one({'type':'username'})
        try:
            username = user["username"].upper()
        except:
            username = user["username"]

        is_return = False
        if names and username in names['rule']:
            flash({'msg':'用户名已存在.', 'type':'w'})
            is_return = True
        else:
            r = mdb_user.db.user.update({"username":user["username"]}, {"$setOnInsert":user}, True)
            if not r["updatedExisting"]:
                flash({'msg':'添加了一个用户.', 'type':'s'})
            else:
                flash({'msg':'用户名已存在.', 'type':'w'})
                is_return = True


        if is_return:
            return redirect(url_for('admin.user_management', state="using"))

        # user profile
        user = mdb_user.db.user.find_one({"username":user["username"]})
        avatar_l = len(config['user'].AVATAR_URL)
        avatar_url = config['user'].AVATAR_URL[randint(0,avatar_l-1)]
        user_profile = {
            'user_id':user["_id"],
            'user_domain':user["_id"],
            'info':'',
            'email':user["email"],
            'avatar_url':avatar_url,
            'addr':{'country':None,'provinces':None, 'city':None,'district':None},
            'tel_num':None,
            "pay":{'alipay':{'use':0}, 'webchatpay':{'use':0}}

        }
        mdb_user.db.user_profile.insert(user_profile)

        # post type
        mdb_cont.db.type.insert({'user_id':user["_id"], 'type':[]})
        mdb_cont.db.type.insert({'user_id':user["_id"], 'tag':[]})
        flash({'msg':'增加了一个新用户: %s.'%(form.username.data),'type':'s'})
        return redirect(url_for('admin.user_management', state="using"))

    return render_template('{}/user/add_user.html'.format(Theme.ADM_THEME_NAME), form=form, view_data=view_data)
    pass


# user management*******************************************************************************************************
@admin.route('/user-management', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def user_management():

    view_data = {'title':u'用户管理', 'page_name':u'用户管理'}

    form = SearchForm()
    form_s = SelectForm()
    form_del = DeleteForm()
    page = request.args.get('page', 1, type=int)
    q = form_s.q.data = request.args.get('q', 'using')
    view_data['state'] = q
    if request.args.get('search_value'):
        search_value = request.args.get('search_value')
        if q == 'using':
            pagination = mongo_paging(mdb_user.db.user,
                         q={"is_delete":False, "username":{"$regex":r".*{}.*".format(search_value)}},
                         field = {"password":0},
                         pre=current_app.config['FLASKY_USERS_PER_PAGE'],
                         page_num=page
                         ,w=current_app.config['FLASKY_USERS_PER_PAGE'], h=1 )
        elif q == 'deleted':
           pagination = mongo_paging(mdb_user.db.user,
                         q={"is_delete":True},
                        field = {"password":0},
                         pre=current_app.config['FLASKY_USERS_PER_PAGE'],
                         page_num=page
                         ,w=current_app.config['FLASKY_USERS_PER_PAGE'], h=1 )
        else:
            abort(404)
    elif q == 'using':
        pagination = mongo_paging(mdb_user.db.user,
                         q={"is_delete":False},
                        field = {"password":0},
                         pre=current_app.config['FLASKY_USERS_PER_PAGE'],
                         page_num=page
                         ,w=current_app.config['FLASKY_USERS_PER_PAGE'], h=1 )
    elif q == 'deleted':
        pagination = mongo_paging(mdb_user.db.user,
                         q={"is_delete":True},
                         field = {"password":0},
                         pre=current_app.config['FLASKY_USERS_PER_PAGE'],
                         page_num=page
                         ,w=current_app.config['FLASKY_USERS_PER_PAGE'], h=1 )
    else:
        abort(404)

    for user in pagination["datas"][0]:
       user["_id"] = str(user["_id"])
       user["role_id"] = mdb_user.db.role.find_one({"_id":ObjectId(user["role_id"])})["name"]
       user["login_info"]=mdb_user.db.user_profile.find_one({'user_id':ObjectId(user["_id"])}, {'last_login_time':1, 'last_login_ip':1})
    view_data['user_list'] = pagination["datas"][0]
    del pagination["datas"]
    view_data['pagination'] = pagination
    view_data['user_count'] = mdb_user.db.user.count()
    now_time = time.time()
    now_time_0 = now_time - now_time%86400
    now_time_7 = now_time - 86400*6
    now_time_30 = now_time - 86400*29
    view_data['count_d'] = mdb_user.db.user.count({"$or":[{"create_at":{"$gt":now_time_0}}, {"create_at":{"$gt":now_time}}]})
    view_data['count_7d'] = mdb_user.db.user.count({"$or":[{"create_at":{"$gt":now_time_7}}, {"create_at":{"$gt":now_time}}]})
    view_data['count_30d'] = mdb_user.db.user.count({"$or":[{"create_at":{"$gt":now_time_30}}, {"create_at":{"$gt":now_time}}]})
    return  render_template('{}/user/user_management.html'.format(Theme.ADM_THEME_NAME),
                            form=form, form_del=form_del,form_s=form_s,
                            view_data = view_data)


# Admin levels: edit user data*****************************************************************************************
@admin.route('/edit-profile/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def edit_profile_admin(id):

    view_data = {'title':u'用户信息编辑'}
    user = mdb_user.db.user.find_one_or_404({"_id":ObjectId(id)}, {"password":0})
    r = mdb_user.db.role.find_one({"_id":ObjectId(user["role_id"])})
    if r["permissions"] & Permission.ROOT and user["active"]:
        flash({'msg':'超级管理员信息不能在此修改.', 'type':'w'})
        return redirect(url_for('admin.user_management', state='using'))
    form = EditProfileAdminForm()
    if form.validate_on_submit():
        user_t = {
            "username":form.username.data.strip(),
            "email":form.email.data,
            "role_id":form.role.data,
            "active":form.is_active.data,
            "update_at":time.time()
        }

        # mdb
        if mdb_user.db.user.find_one({"username":user_t["username"], "_id":{"$ne":user["_id"]}}):
            flash({'msg':'%s 信息修改失败,名字已存在.'%(user["username"]), 'type':'w'})
        elif mdb_user.db.user.find_one({"email":user_t["email"], "_id":{"$ne":user["_id"]}}):
            flash({'msg':'%s 信息修改失败,email已存在.'%(user["username"]), 'type':'w'})
        else:
            mdb_user.db.user.update({"_id":user["_id"]}, {"$set":user})
            flash({'msg':'%s 信息修改成功.'%(user["username"]), 'type':'s'})
        return redirect(url_for('admin.user_management', state='using'))
    form.username.data = user["username"]
    form.email.data = user["email"]
    form.role.data = user["role_id"]
    form.role.data = user["role_id"]
    form.is_active.data = user["active"]
    return  render_template('{}/user/edit_profile_admin.html'.format(Theme.ADM_THEME_NAME), form=form, user_id=user["_id"], view_data=view_data)


# Admin levels: edit user data*****************************************************************************************
@admin.route('/password-reset/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def password_reset_admin(id):

    view_data = {'title':u'修改用户密码'}
    user = mdb_user.db.user.find_one_or_404({"_id":ObjectId(id)})
    r = mdb_user.db.role.find_one({"_id":ObjectId(user["role_id"])})
    if r["permissions"] & Permission.ROOT:
        flash({'msg':'超级管理员密码不能在此修改.', 'type':'w'})
        return redirect(url_for('admin.user_management', state='using'))
    form = PasswordResetAdmin()

    if form.validate_on_submit():
        user = User(user)
        user_t = {
            "password":user.generate_password_hash(form.password.data)
        }
        mdb_user.db.user.update({"_id":ObjectId(user.id)}, {"$set":user_t})
        flash({'msg':'%s 重设了密码.'%(user.username), 'type':'s'})
        return redirect(url_for('admin.user_management', state='using'))

    return  render_template('{}/user/password_reset_admin.html'.format(Theme.ADM_THEME_NAME), form=form,
                            username=user["username"],
                            view_data=view_data)


# Delete Admin*********************************************************************************************************
@admin.route('/delete-user', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def delete_user():

    form_del = DeleteForm()
    if form_del.validate_on_submit():
        action = form_del.action.data
        id_list = request.form.getlist("boolean")
        id_len = len(id_list)
        if action=='delete':
            for id in id_list:
                if id == 'y':
                    id_len -= 1
                    continue
                user = mdb_user.db.user.find_one_or_404({"_id":ObjectId(id)})
                if mdb_user.db.role.find_one({"_id":ObjectId(user["role_id"])})["permissions"] & Permission.ROOT:
                    flash({'msg':'超级管理员不能删除.', 'type':'w'})
                    id_len -= 1
                else:
                    mdb_user.db.user.update({"_id":user["_id"]}, {"$set":{"is_delete":True}})

            flash({'msg':'{}个用户已被删除.'.format(id_len), 'type':'s'})
            return redirect(url_for('admin.user_management', state='using'))


        elif action=='recover':
            for id in id_list:
                if id == 'y':
                    id_len -= 1
                    continue
                user = mdb_user.db.user.find_one_or_404({"_id":ObjectId(id)})
                mdb_user.db.user.update({"_id":user["_id"]}, {"$set":{"is_delete":False}})
            flash({'msg':'{}个用户已恢复.'.format(id_len), 'type':'s'})
            return redirect(url_for('admin.user_management', state='deleted'))
        else:
            abort(404)
    else:
        abort(404)



# Role management******************************************************************************************************
@admin.route('/add-role', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def add_role():
    view_data = {}
    form =RoleForm()
    if form.validate_on_submit():
        r = 0x0
        for i in form.permissions.data:
            r = r | i

        role = {
            "name":form.name.data,
            "permissions":r,
            "default":form.default.data,
            "instructions":form.instructions.data
        }
        r = mdb_user.db.role.update({"name":role["name"]}, {"$setOnInsert":role}, True)
        if not r["updatedExisting"]:
            flash({'msg':'添加了一个角色.', 'type':'s'})
        else:
            flash({'msg':'角色名已存在.', 'type':'w'})
        return redirect(url_for('admin.role_management'))
    view_data['op_type'] = 'add'
    return render_template('{}/user/add_role.html'.format(Theme.ADM_THEME_NAME), form=form , view_data=view_data)


# Role management******************************************************************************************************
@admin.route('/role-management', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def role_management():

    view_data = {"page_name":u"角色管理", 'title':u"角色管理"}
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    if request.args.get('search_value'):
        search_value = request.args.get('search_value')
        pagination = mongo_paging(mdb_user.db.role,
                         q={"is_delete":True, "name":{{"$regex":".*{}.*".format(search_value)}}},
                         pre=current_app.config['FLASKY_USERS_PER_PAGE'],
                         page_num=page
                         ,w=current_app.config['FLASKY_USERS_PER_PAGE'], h=1 )
    else:
        pagination = mongo_paging(mdb_user.db.role,
                         pre=current_app.config['FLASKY_USERS_PER_PAGE'],
                         page_num=page
                         ,w=current_app.config['FLASKY_USERS_PER_PAGE'], h=1 )
    view_data['role_list'] = pagination["datas"][0]
    print pagination["datas"][0]
    view_data['pagination'] = pagination
    return  render_template('{}/user/role_management.html'.format(Theme.ADM_THEME_NAME), form=form, view_data=view_data)


# Edit Role*************************************************************************************************************
@admin.route('/edit-role/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def edit_role(id):

    view_data = {}
    role = mdb_user.db.role.find_one({"_id":ObjectId(id)})
    form =RoleForm()
    if form.validate_on_submit():
        r = 0b0
        for i in form.permissions.data:
            r = r | i
        if role["permissions"] & Permission.ROOT:
            r = Permission.ROOT
        role_t = {
            "name":form.name.data.strip(),
            "default":form.default.data,
            "instructions":form.instructions.data,
            "permissions":r,

        }

        r = mdb_user.db.role.find_one({"name":role["name"], "_id":{"$ne":role["_id"]}})
        if r:
            flash({'msg':'更新失败!角色名字存在.'.format(role.name), 'type':'w'})
        else:
            mdb_user.db.role.update({"_id":ObjectId(role["_id"])}, {"$set":role_t})
            flash({'msg':'角色 {} 信息修改成功.'.format(role["name"]), 'type':'s'})
        return redirect(url_for('admin.role_management'))
    form.name.data = role["name"]
    form.default.data = role["default"]
    form.permissions.data = [role["permissions"]]
    form.instructions.data = role["instructions"]
    view_data['op_type'] = 'edit'
    return render_template('{}/user/add_role.html'.format(Theme.ADM_THEME_NAME), form=form, view_data=view_data)



# Delete Role***********************************************************************************************************
@admin.route('/role-contains/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def role_contains(id):
    view_data = {}
    form = SearchForm()
    form_del = DeleteForm()
    page = request.args.get('page', 1, type=int)
    if request.args.get('search_value'):
        search_value = request.args.get('search_value')
        pagination = mongo_paging(mdb_user.db.user,
                         q={"is_delete":False, "role_id":ObjectId(id), "username":{"$regex":".*{}.*".format(search_value)}},
                         field = {"password":0},
                         pre=current_app.config['FLASKY_USERS_PER_PAGE'],
                         page_num=page
                         ,w=current_app.config['FLASKY_USERS_PER_PAGE'], h=1 )

    else:
        pagination = mongo_paging(mdb_user.db.user,field = {"password":0},
                         q={"is_delete":False, "role_id":id},

                         pre=current_app.config['FLASKY_USERS_PER_PAGE'],
                         page_num=page
                         ,w=current_app.config['FLASKY_USERS_PER_PAGE'], h=1 )
    for user in pagination["datas"][0]:
       user["_id"] = str(user["_id"])
       user["role_id"] = mdb_user.db.role.find_one({"_id":ObjectId(user["role_id"])})["name"]
       user["login_info"]=mdb_user.db.user_profile.find_one({'user_id':ObjectId(user["_id"])}, {'last_login_time':1, 'last_login_ip':1})
    view_data['user_list'] = pagination["datas"][0]
    del pagination["datas"]
    view_data['pagination'] = pagination
    view_data['page_name'] = mdb_user.db.role.find_one({"_id":ObjectId(id)})["name"]
    view_data['role_id'] = id
    return  render_template('{}/user/role_contains.html'.format(Theme.ADM_THEME_NAME), form=form, form_del=form_del, view_data=view_data)
