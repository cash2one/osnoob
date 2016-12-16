#-*-coding:utf-8-*-
import time
from flask_login import current_user
from apps import mdb, cache
from apps.admin.models.user import Permission
from apps.blueprint import online
from apps.config import config
from apps.multimedia.process.image import find_imgs
from apps.post.process.post import p_posts, recommend_posts, post_types, post_tags, new_comments
from apps.verify.process.ver_code import create_code
from flask import render_template, url_for, request, g, send_file, flash
from werkzeug.utils import redirect

# **********************************************************************************************************************
@online.route('/robots.txt', methods=['GET', 'POST'])
def robots():

    return  send_file('templates/file/robots.txt')

# **********************************************************************************************************************
@online.route('/', methods=['GET', 'POST'])
def index():
    request.cache_control
    sort_f = [('time',-1)]
    sort_f_r = [('praise',-1),('pv',-1)]
    _filter = {'status':1, 'subject':{'$ne':'sys'}, "pv":{"$gte":config['post'].NEW_PV}}
    if g.tn == "pc":
        view_data = p_posts(request, filter=_filter, sort = sort_f)
        # 类型
        view_data['post_types'] = post_types()
        # 标签
        view_data['post_tags'] = post_tags()
        view_data['title'] = config['title'].HOME_TITLE_PC
    else:
        view_data = p_posts(request, filter=_filter, sort = sort_f, pre=8)
        view_data['title'] = config['title'].HOME_TITLE_M
        view_data['home'] = True


    # 推荐
    view_data['recommend'] = recommend_posts(sort_f_r)
    # 最新评论
    view_data['new_comment'] = new_comments()
    # 顶部展示
    view_data['home_top_shows'] = find_imgs(filter={'type':'show', "url.key":{"$regex":"home-top"}})
    view_data['home_r_shows'] = find_imgs(filter={'type':'show', "url.key":{"$regex":"home-r"}})
    view_data['shows_cnt'] = range(0, len(view_data['home_top_shows']))
    view_data['profile']={'user_id':'all'}

    # 公告
    view_data['inform'] = inform()
    view_data['is_home'] = True
    return render_template('index.html', view_data = view_data)

@cache.cached(timeout=config['cache_timeout'].POSTS, key_prefix="inform_")
def inform():
    inform = mdb.db.posts.find_one({'subject':'sys', 'type':'系统通知', 'status':1}, {'body':0})
    if inform:
        inform['username'] = mdb.db.user_profile.find_one({'user_id':inform['user_id']})['username']
    return inform


# **********************************************************************************************************************
#　伪装后台
@online.route('/admin/sign-in', methods=['GET', 'POST'])
@cache.cached()
def fake_login():


    view_data = {'login_type':'c', 'title':'登录管理台'}
    if current_user.is_authenticated() and current_user.can(Permission.AUDITOR):
        return redirect(url_for('admin.index'))
    elif request.method == 'POST':
        flash({"type":"e", "msg":u"账号或密码错误!"})
    return render_template('online/login_f.html', view_data=view_data)


#　伪装后台
@online.route('/admin', methods=['GET', 'POST'])
@cache.cached()
def fake_admin():

    return redirect(url_for('online.fake_login'))


