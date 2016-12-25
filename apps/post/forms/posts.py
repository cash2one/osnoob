#-*-coding:utf-8-*-
from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField, FileField
from wtforms.validators import Required, Length
from apps import mdb_sys

__author__ = 'woo'

class EditPost(Form):

    title = StringField(u'标题', validators=[Required(), Length(1, 128)])
    body = TextAreaField(u'正文')
    boolean_l = BooleanField(u'标签')
    s_type = SelectField(u'分类', coerce=str)

    issue = SubmitField(u'发布')
    draft = SubmitField(u'存稿')
    def __init__(self, subject,*args, **kwargs):
        super(EditPost, self).__init__(*args, **kwargs)
        self.s_type.choices = [(u'其他', u'其他')]
        t_list = [(t, t)
                             for t in mdb_sys.db.type.find_one({'project':"post-type", 'subject':subject})['type']]
        self.s_type.choices.extend(t_list)
