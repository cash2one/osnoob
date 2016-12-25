#-*-coding:utf-8-*-
from flask import flash
from flask_login import current_user
from flask_wtf import Form
from wtforms import  PasswordField, StringField, SubmitField, FileField,SelectField
from wtforms.validators import Required, Length,  Email, EqualTo
from wtforms import  ValidationError
from apps import mdb_user

__author__ = 'woo'
'''
User Form
'''

# *********************************************************************************************************************
class PasswordResetForm(Form):

    '''
    password reset form
    '''

    old_password = PasswordField('原密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='确认密码必须一致哦！')
    ])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('提交修改')

    def validate_password(self, field):
        if len(field.data) < 8 :
            raise ValidationError('密码至少8个字符哦！')

        too_simple = True
        last_ac = False
        for p in field.data:
            _ac = ord(p)
            if last_ac:
                if _ac != last_ac+1:
                    too_simple = False
                    break
            last_ac = _ac
        if too_simple:
            flash({'type':'w','msg':u'密码太简单,不能取连续字符！'})


# **********************************************************************************************************************
class EditRewardForm(Form):

    '''
    User levels: edit user data
    '''

    payimg = FileField(u'二维码')
    pay_type = SelectField(u'应用商', coerce=str)
    word = StringField(u'说点什么', validators=[Required(), Length(1, 64)])
    nonuse = SelectField(u'打赏', coerce=str)
    password = PasswordField('登录密码',validators=[Required()])
    submit = SubmitField(u'保存修改')

    def __init__(self, op, *args, **kwargs):
        super(EditRewardForm, self).__init__(*args, **kwargs)
        user = mdb_user.db.user_profile.find_one_or_404({'user_id':current_user.id})
        pay_list = [('alipay', '支付宝'), ('wechatpay', '微信支付')]
        if op=="edit" or not 'pay' in user:
            self.pay_type.choices = pay_list
        elif 'pay' in user:
            if 'alipay' in user['pay'] and 'wechatpay' in user['pay']:
                pay_list = []
            elif 'alipay' in user['pay']:
                pay_list = [('wechatpay', '微信支付')]
            elif 'wechatpay' in user['pay']:
                pay_list = [('alipay', '支付宝')]
            self.pay_type.choices = pay_list


        self.nonuse.choices = [(1, '使用'), (0, '禁用')]


# **********************************************************************************************************************
class EmailChangeForm(Form):

    '''
    User levels: edit user data
    '''

    email = StringField('Email', validators=[Required(), Length(1, 64), Email(u'邮箱格式不对哦')])
    password = PasswordField('登录密码',validators=[Required()])

    submit = SubmitField('保存修改')

    def validate_email(self, field):
        user = mdb_user.user.find_one({"email":field.data})
        if  user and user["_id"] != current_user.id:
            raise ValidationError('邮箱{}在本站注册过哦.'.format(field.data))






