#-*-coding:utf-8-*-
from flask_wtf import Form
from wtforms import TextAreaField, StringField, SelectField, SubmitField, BooleanField, HiddenField
from wtforms.validators import Required, Length

__author__ = 'woo'

# **********************************************************************************************************************
class AddPostTypeForm(Form):

    '''
    IMG
    '''
    project = StringField('项目', validators=[Required(), Length(1, 64)])
    subject = StringField('类型', validators=[Required(), Length(1, 64)])
    value = TextAreaField('值', validators=[Required()])
    submit = SubmitField("保存")



class PostTypeDelForm(Form):

    '''
    img
    '''
    boolean = BooleanField()
    op_type = SelectField(coerce=str)
    q = HiddenField()
    submit = SubmitField('应用')
    def __init__(self, *args, **kwargs):
        super(PostTypeDelForm, self).__init__(*args, **kwargs)
        self.op_type.choices = [('delete', u'删除')]

