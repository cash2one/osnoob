#-*-coding:utf-8-*-
import time
from datetime import datetime
from werkzeug.exceptions import abort
from apps.multimedia.process.image import find_imgs
from apps.online.process.user import user_edit_profile
from apps.shared_tool.image_up import img_up, img_del
from apps.blueprint import online
from apps.shared_tool.email.token import generate_confirmation_token, confirm_token
from apps.verify.process.ver_code import create_code
from flask import  render_template, redirect, request, url_for, flash, session, Markup
from flask_login import current_user, login_required, logout_user,login_user
from flask_mail import Message
from apps import db, mdb, config, mdb_sys
from apps.admin.models.user import User
from apps.online.forms.user import EditRewardForm
from apps.shared_tool.email.send_email import send_email

__author__ = 'woo'
'''
ONLINE VIEWS
'''

# *********************************************************************************************************************
@online.route('/show/<table>', methods=['GET', 'POST'])
def h5(table):

    data = find_imgs(filter={'type':'show', "url.key":{"$regex":"h5-{}".format(table)}})
    if data:
        print data
        return redirect(data[0]['link'])
    else:
        abort(404)

# *********************************************************************************************************************
@online.route('/sign-up', methods=['GET', 'POST'])
def register():
    view_data = {'title':'注册-{}'.format(config['title'].TITLE)}

    # 验证码
    _code = create_code()
    view_data['code'] = _code
    return render_template('online/user/register.html', view_data=view_data)


# **********************************************************************************************************************
@online.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:

        flash({'msg':config['email'].LOSE_VER_HTML.format(
            url_for('online.resend_confirmation',email=email)),
            'type':'w'})
        return redirect(url_for('online.login'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.active:
        flash({'msg':'您的账户已验证过邮箱,请登录', 'type':'s'})
        return redirect(url_for('online.login'))
    else:
        user.active = True
        user.confirmed_on = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        #
        login_user(user, False)
        flash({'msg':'<p>邮箱验证成功, 首次登录成功,请修改信息.<a style="color:#428bca;" href="/">先不管它</a>！</p>', 'type':'s'})
        return redirect(url_for('online.account'))




# **********************************************************************************************************************
@online.route('/resend/<email>')
def resend_confirmation(email):
    User.query.filter_by(email=email, active=0).first_or_404()
    token = generate_confirmation_token(email)
    confirm_url = url_for('online.confirm_email', token=token, _external=True)
    html = render_template('online/email/activate.html', confirm_url=confirm_url)

    # send email
    msg = Message("{}注册验证".format(config['email'].MAIL_PROJECT),
                  sender=config['email'].MAIL_DEFAULT_SENDER,
                  recipients=[email])
    msg.html = html
    send_email(mdb_sys.db,msg)

    flash({'msg':'新的验证邮件已发送,请查收验证！.', 'type':'s'})
    return redirect(url_for('online.login'))


# **********************************************************************************************************************
@online.route('/sign-in', methods=['GET', 'POST'])
def login():
    view_data = {'login_type':'f'}
    Markup('''<meta property="qc:admins" content="14111676166677276375" />''')
    if current_user.is_authenticated():
        return redirect(url_for('online.index'))
    return render_template('online/login.html',view_data=view_data)


# **********************************************************************************************************************
@online.route('/logout')
@login_required
def logout():
    session.pop('qq_token', None)
    logout_user()
    return redirect(request.args.get('next') or url_for('online.index'))

# **********************************************************************************************************************
@online.route('/accounts', methods=['GET','POST'])
@login_required
def account():
    view_data = {'title':'个人信息-{}'.format(config['title'].TITLE)}
    if request.method == 'POST':
        uploaded_files = request.files.getlist("avatar")
        username = request.form['username'].strip()
        try:
            sex = request.form['sex']
        except:
            sex = None

        addr = {'p':request.form['p'], 'c':request.form['c'], 'a':request.form['a']}
        info = request.form['info'].strip()
        user_edit_profile(uploaded_files, username, sex, addr, info)
        return redirect(url_for('online.account'))

    profile = mdb.db.user_profile.find_one_or_404({'user_id':current_user.id})
    # 头像
    view_data['ava_url'] = profile['avatar_url']
    # 姓名
    view_data["username"] = current_user.username
    view_data["user_domain"] = profile['user_domain']
    view_data['email'] = profile['email'].strip()
    if view_data['email'] in config['oauth_login'].EMAIL_LIST:
        view_data['email'] = u"第三方账号登录,请先修改邮箱"

    if 'sex' in profile:
        if profile['sex'] == 0:
            view_data["m"] = True
        elif profile['sex'] == 1:
            view_data["f"] = True
    view_data['info'] = profile['info'].strip()
    return  render_template('online/user/user.html', view_data=view_data)


# **********************************************************************************************************************
@online.route('/accounts/password-reset', methods=['GET', 'POST'])
@login_required
def password_reset():

    if current_user.email.strip() in config['oauth_login'].EMAIL_LIST:
        flash({"msg":u"请先绑定邮箱, 用于找回密码！", "type":'w'})
        return redirect(url_for("online.account"))

    view_data = {'title':'密码修改-{}'.format(config['title'].TITLE)}
    profile = mdb.db.user_profile.find_one_or_404({'user_id':current_user.id})
    if 'is_oauth_first_change' in profile and profile['is_oauth_first_change']:
        view_data['is_oauth_first_change'] = True
    return render_template('online/user/password_reset.html', view_data=view_data)


# User levels: edit user data*******************************************************************************************
@online.route('/accounts/pre-email-change', methods=['GET', 'POST'])
@login_required
def email_change():

    view_data = {'title':'邮箱修改-{}'.format(config['title'].TITLE)}
    return  render_template('online/user/email_change.html',  view_data=view_data)


# User levels: edit user data*******************************************************************************************
@online.route('/accounts/retrieve-password', methods=['GET', 'POST'])
def retrieve_password():

    view_data = {'title':'找回密码-{}'.format(config['title'].TITLE)}
    # 验证码
    _code = create_code()
    view_data['code'] = _code

    return  render_template('online/user/ret_password.html', view_data=view_data)

# ------------------------------------------------------------------------------------------------------
@online.route('/accounts/reward', methods=['GET', 'POST'])
@login_required
def reward():
    view_data = {'title':'打赏-{}'.format(config['title'].TITLE)}
    profile = mdb.db.user_profile.find_one_or_404({'user_id':current_user.id})
    if 'pay' in profile and profile['pay']:
        view_data['pay'] = profile['pay']
        pay_cnt = 0
        for k in profile['pay']:
            if "url" in profile['pay'][k]:
                pay_cnt += 1
        view_data['pay_cnt'] = pay_cnt
    else:
        view_data['pay'] = {}
        view_data['pay_cnt'] = 0
    return  render_template('online/user/reward.html', view_data=view_data)

# ------------------------------------------------------------------------------------------------------
@online.route('/accounts/reward/add', methods=['GET', 'POST'])
@login_required
def reward_add():
    view_data = {'title':'添加打赏-{}'.format(config['title'].TITLE)}
    profile = mdb.db.user_profile.find_one_or_404({'user_id':current_user.id})
    form = EditRewardForm('add')
    if form.submit.data:
        if current_user.verify_password(form.password.data):
            bucket_name = {'b':config['upload'].IMG_B, 'domain':'img', 'project':'pay'}
            uploaded_files = request.files.getlist("payimg")
            r = img_up(uploaded_files, bucket_name)
            if r['url'] != -1 and r['url'] != 1:
                if 'pay' in profile and profile['pay']:
                    _pay = profile['pay']
                    _pay[form.pay_type.data] = {'url':r['url'], 'word':form.word.data.strip(), 'status':0, 'time':time.time()}
                else:
                    _pay = {form.pay_type.data:{'url':r['url'], 'word':form.word.data.strip(), 'status':0, 'time':time.time()}}
                flash({'msg':'二维码上传成功,需要等待审核！', 'type':'s'})
            else:
                flash({'type':'e', 'msg':'支付二维码上传失败!'})
                return  render_template('online/user/reward_edit.html', view_data=view_data, form=form)

            _pay[form.pay_type.data]['use'] = int(form.nonuse.data)
            _pay[form.pay_type.data]['time'] = time.time()
            mdb.db.user_profile.update({'user_id':current_user.id}, {'$set':{'pay':_pay}})
            return  redirect(url_for('online.reward'))
        else:
            flash({'msg':'登录密码不对!', 'type':'e'})

    view_data['pay_url'] = {}
    return  render_template('online/user/reward_edit.html', view_data=view_data, form=form)


# ------------------------------------------------------------------------------------------------------
@online.route('/accounts/reward/edit/<type>', methods=['GET', 'POST'])
@login_required
def reward_edit(type):
    view_data = {'title':'打赏设置-{}'.format(config['title'].TITLE)}
    profile = mdb.db.user_profile.find_one_or_404({'user_id':current_user.id})
    form = EditRewardForm('edit')
    if form.submit.data:
        if current_user.verify_password(form.password.data):
            bucket_name = {'b':config['upload'].IMG_B, 'domain':'img', 'project':'pay'}
            uploaded_files = request.files.getlist("payimg")
            r = img_up(uploaded_files, bucket_name)
            if r['url'] != -1 and r['url'] != 1:
                img_del(profile['pay'][type.strip()]['url'])
                if 'pay' in profile:
                    _pay = profile['pay']
                    _pay[type.strip()] = {'url':r['url'], 'word':form.word.data.strip(), 'status':0, 'time':time.time()}
                else:
                    _pay = {type.strip():{'url':r['url'], 'word':form.word.data.strip(), 'status':0, 'time':time.time()}}
                flash({'msg':'修改了二维码,需要等待审核！', 'type':'s'})
            else:
                if 'pay' in profile:
                    _pay = profile['pay']
                    status = _pay[type.strip()]['status']
                    _pay[type.strip()] = {'url':_pay[type.strip()]['url'], 'word':form.word.data.strip(), 'status':status}
                else:
                    _pay = {type.strip():{'url':'', 'word':form.word.data.strip(), 'status':0}}
            _pay[type.strip()]['use'] = int(form.nonuse.data)
            _pay[type.strip()]['time'] = time.time()
            mdb.db.user_profile.update({'user_id':current_user.id}, {'$set':{'pay':_pay}})
            return  redirect(url_for('online.reward'))
        else:
            flash({'msg':'登录密码不对!', 'type':'e'})

    form.pay_type.data = type.strip()
    form.word.data = profile['pay'][type.strip()]['word']
    form.nonuse.data = str(profile['pay'][type.strip()]['use'])
    view_data['pay_url'] = profile['pay'][type.strip()]['url']
    view_data['op_type'] = 'edit'
    return  render_template('online/user/reward_edit.html', view_data=view_data, form=form)