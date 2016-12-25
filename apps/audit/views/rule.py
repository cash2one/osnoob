#-*-coding:utf-8-*-
from apps import mdb_sys
from apps.audit.forms.rule import RuleDelForm, EditRuleForm, AddRuleForm
from apps.blueprint import audit
from bson import ObjectId
from flask import render_template, request, flash, url_for
from flask_login import login_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from apps.config import Permission
from apps.shared_tools.decorator.decorators import permission_required

__author__ = 'woo'

# *********************************************************************************************************************
# 规则管理
@audit.route('/rules', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def rules():
    view_data = {'title':'内容审核', 'page_name':'内容审核规则管理'}
    form_del = RuleDelForm()
    view_data['rules'] = mdb_sys.db.audit_rules.find()
    return render_template('audit/rule/rule.html', view_data=view_data, form_del=form_del)


# *********************************************************************************************************************
# 规则编辑
@audit.route('/rule/add', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def rule_add():
    view_data = {'title':'审核规则添加', 'page_name':'内容审核规则添加'}
    form = AddRuleForm()
    if form.submit.data:
        rule = {
            'type':form.name.data.strip(),
            'rule':form.rules.data.strip().split(";")
        }

        mdb_sys.db.audit_rules.insert(rule)
        return redirect(url_for('audit.rules'))

    return render_template('audit/rule/rule_edit.html', view_data=view_data, form=form)

# *********************************************************************************************************************
# 规则编辑
@audit.route('/rule/edit/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def rule_edit(id):
    view_data = {'title':'审核规则编辑', 'page_name':'内容审核规则编辑'}
    form = EditRuleForm()
    if form.submit.data:
        rule_list = form.rules.data.strip().split(";")
        mdb_sys.db.audit_rules.update({'_id':ObjectId(id)}, {'$set':{'rule':rule_list}})
        return redirect(url_for('audit.rules'))
    rule = mdb_sys.db.audit_rules.find_one_or_404({'_id':ObjectId(id)})
    view_data['name'] = rule['type']
    _str = ""
    for k in rule['rule']:
        _str = "{};{}".format(_str, k.strip())
    form.rules.data = _str.strip(";")
    return render_template('audit/rule/rule_edit.html', view_data=view_data, form=form)

# *********************************************************************************************************************
# 规则删除
@audit.route('/rule/delete', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def delete_rule():

    form_del = RuleDelForm()
    if form_del.submit.data:
        id_list = request.form.getlist("boolean")
        id_len = len(id_list)
        op_type = form_del.op_type.data
        if op_type=='delete':
            for id in id_list:
                if id == 'y':
                    id_len -= 1
                    continue
                mdb_sys.db.audit_rules.remove({'_id':ObjectId(id)})
            flash({'msg':u'删除了{}条规则'.format(id_len), 'type':'s'})

        return redirect(url_for('audit.rules'))
    abort(404)

