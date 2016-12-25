# -*-coding:utf-8-*-
from flask_wtf import Form
from wtforms import TextAreaField, HiddenField, SubmitField, StringField
from wtforms.validators import Required, Length, Email

__author__ = 'woo'


# **********************************************************************************************************************
class CommentForm(Form):

    '''
    Comment form
    '''

    username = StringField(u'用户', validators=[Length(0, 64)])
    email = StringField(u'邮箱', validators=[Length(0, 64), Email(u'邮箱格式不对哦！')])
    comment = TextAreaField('评论')
    user_id = HiddenField()
    case_id = HiddenField()
    reply_id = HiddenField()
    submit = SubmitField(u'评上去')

    praise_btn = SubmitField()



# **********************************************************************************************************************
class Delete(Form):
    '''
    delete
    '''
    thing_type = HiddenField()
    other = HiddenField()
    id = HiddenField()
    del_btn = SubmitField('删除')





