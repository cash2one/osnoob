#-*-coding:utf-8-*-
from flask_wtf import Form
from wtforms import  SelectField,  BooleanField,  SubmitField,HiddenField, ValidationError, StringField
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
    submit = SubmitField('搜索:标题')

    def validate_search_value(self, field):
        if field.data is None:
            raise ValidationError('请输入关键字搜索.')

# *********************************************************************************************************************
class DeleteForm(Form):

    boolean = BooleanField()
    q = HiddenField()
    op_type = SelectField(coerce=str)
    submit = SubmitField('应用')
    def __init__(self, *args, **kwargs):
        super(DeleteForm, self).__init__(*args, **kwargs)
        self.op_type.choices = [('pass', u'通过'),('no_pass', u'不通过'),('delete', u'移除'),('recover', u'恢复'),
                                ('delete_rec',u'永久删除')]

# *********************************************************************************************************************
class SelectForm(Form):

    q = SelectField(coerce=str)
    submit = SubmitField('选择')

    def __init__(self, *args, **kwargs):
        super(SelectForm, self).__init__(*args, **kwargs)
        self.q.choices = [('all', u'全部'),('been', u'已发表'),('audit', u'待审核'),('auto_audit', u'已自动审核'),
                          ('draft', u'存稿'),('unqualified', u'未通过'),
                          ('deleted', u'回收站')]
