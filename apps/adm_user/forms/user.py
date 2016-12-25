#-*-coding:utf-8-*-
from apps import mdb_user
from flask_wtf import Form
from wtforms import SelectMultipleField, SelectField, PasswordField, BooleanField, StringField, SubmitField, TextAreaField, \
    HiddenField
from wtforms.validators import Required, Length, Email, EqualTo
from wtforms import  ValidationError
from apps.config import Permission

__author__ = 'woo'
'''
User Form
'''


# **********************************************************************************************************************
class EditProfileAdminForm(Form):

    '''
    Admin levels: edit user data
    '''

    username = StringField(u'用户名', validators=[
        Required(), Length(1, 64)])
    email = StringField(u'Email', validators=[Required(), Length(1, 64), Email(u'邮箱格式不对哦.')])
    role = SelectField(u'角色', coerce=str)
    is_active = BooleanField(u'激活')
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(str(role["_id"]), role["name"])
                             for role in mdb_user.db.role.find({})]



# **********************************************************************************************************************
class PasswordResetAdmin(Form):

    '''
    Admin level:reset password
    '''

    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='两次密码不一致，请重新输入.')
    ])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('重设')

    def validate_password(self, field):
        if len(field.data) < 8 :
            raise ValidationError(u'密码必须不少于８个字符.')

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

# **********************************************************************************************************************
class AddUserForm(Form):

    '''
    register form
    '''

    username = StringField(u'用户', validators=[
        Required(), Length(1, 64)])
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email(u'邮箱格式不对哦！')])
    password = PasswordField(u'密码', validators=[
        Required(), EqualTo('password2', message='两次密码不一致，请重新输入.')
    ])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    role = SelectField('角色', coerce=str)
    submit = SubmitField('注册')

    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(str(role["_id"]), role["name"])
                             for role in mdb_user.db.role.find({})]

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError(u'密码必须不少于８个字符.')

# **********************************************************************************************************************
class RoleForm(Form):

    '''
    add role form
    '''

    name = StringField('角色名字', validators=[
        Required(), Length(1, 64)])
    permissions = SelectMultipleField('权限', coerce=int)
    default = BooleanField('是否时默认角色')
    instructions = TextAreaField('说明')
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        self.permissions.choices = Permission.one_list


# *********************************************************************************************************************
class DeleteForm(Form):

    boolean = BooleanField()
    action = HiddenField()
    submit = SubmitField()

# *********************************************************************************************************************
class SelectForm(Form):

    q = SelectField(coerce=str)
    submit = SubmitField('应用')

    def __init__(self, *args, **kwargs):
        super(SelectForm, self).__init__(*args, **kwargs)
        self.q.choices = [('using', u'正常用户'),('deleted', u'已冻结用户')]
