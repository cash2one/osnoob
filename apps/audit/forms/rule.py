#-*-coding:utf-8-*-
from apps import mdb_sys
from flask_wtf import Form
from wtforms import TextAreaField, StringField, SelectField, SubmitField, BooleanField, HiddenField, ValidationError
from wtforms.validators import Required, Length

__author__ = 'woo'

# **********************************************************************************************************************
class AddRuleForm(Form):

    '''
    IMG
    '''
    name = StringField('类型', validators=[Required(), Length(1, 64)])
    rules = TextAreaField('规则', validators=[Required()])
    submit = SubmitField("保存")

    def validate_name(self, field):
        rule = mdb_sys.db.audit_rules.find_one({'type':field.data})
        if  rule:
            raise ValidationError('此名字已存在！')

# **********************************************************************************************************************
class EditRuleForm(Form):

    '''
    IMG
    '''
    rules = TextAreaField('规则', validators=[Required()])
    submit = SubmitField("保存")


class RuleDelForm(Form):

    '''
    img
    '''
    boolean = BooleanField()
    op_type = SelectField(coerce=str)
    q = HiddenField()
    submit = SubmitField('应用')
    def __init__(self, *args, **kwargs):
        super(RuleDelForm, self).__init__(*args, **kwargs)
        self.op_type.choices = [('delete', u'删除')]
