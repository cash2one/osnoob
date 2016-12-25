#-*-coding:utf-8-*-
from apps import mdb_sys
from flask_wtf import Form
from wtforms import FileField, StringField, SelectField, SubmitField, BooleanField, HiddenField
from wtforms.validators import Required, Length

__author__ = 'woo'

# **********************************************************************************************************************
class EditImgForm(Form):

    '''
    IMG
    '''

    img = FileField('图片')
    name = StringField('名字', validators=[Required(), Length(1, 64)])
    showname = StringField('展示名字', validators=[Required(), Length(1, 64)])
    info = StringField('说明', validators=[Required(), Length(1, 64)])
    link = StringField('链接', validators=[Required(), Length(1, 64)])
    project = SelectField(u'项目', coerce=str)
    submit = SubmitField("保存")

    def __init__(self, *args, **kwargs):
        super(EditImgForm, self).__init__(*args, **kwargs)
        self.project.choices = self.project.choices = [(tp[0], tp[1]) for tp in mdb_sys.db.type.find_one({"project":'image', "subject":"page-show"})["type"]]

class ImgForm(Form):
    '''
    img
    '''

    project = SelectField(coerce=str)
    submit = SubmitField('选择')
    def __init__(self, *args, **kwargs):
        super(ImgForm, self).__init__(*args, **kwargs)
        self.project.choices = [(tp[0], tp[1]) for tp in mdb_sys.db.type.find_one({"project":'image', "subject":"page-show"})["type"]]

class ImgDelForm(Form):

    '''
    img
    '''
    boolean = BooleanField()
    op_type = SelectField(coerce=str)
    q = HiddenField()
    submit = SubmitField('应用')
    def __init__(self, *args, **kwargs):
        super(ImgDelForm, self).__init__(*args, **kwargs)
        self.op_type.choices = [('delete', u'删除')]
