#-*-coding:utf-8-*-
from flask_wtf import Form
from wtforms import  SelectField, SubmitField,HiddenField, ValidationError, StringField, BooleanField
from wtforms.validators import Required, Length

__author__ = 'woo'
# **********************************************************************************************************************
class SearchForm(Form):

    '''
    Search
    '''
    search_value = StringField(validators=[
        Required(), Length(1, 64), ])
    q = HiddenField()
    submit = SubmitField('搜索')

    def validate_search_value(self, field):
        if field.data is None:
            raise ValidationError('请输入关键字搜索.')


# *********************************************************************************************************************
class SelectForm(Form):

    q = SelectField(coerce=str)
    submit = SubmitField('选择')

    def __init__(self, *args, **kwargs):
        super(SelectForm, self).__init__(*args, **kwargs)
        self.q.choices = [('all', u'全部'),('audit', u'待审核'),('unqualified', u'未通过'),('pass',u'通过')]


# *********************************************************************************************************************
class DeleteForm(Form):

    boolean = BooleanField()
    q = HiddenField()
    op_type = SelectField(coerce=str)
    submit = SubmitField('应用')
    def __init__(self, *args, **kwargs):
        super(DeleteForm, self).__init__(*args, **kwargs)
        self.op_type.choices = [('pass', u'通过'),('no_pass', u'不通过')]

