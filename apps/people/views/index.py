#-*-coding:utf-8-*-
from apps import cache, mdb_user
from apps.blueprint import people
from apps.post.process.post import p_posts, post_tags
from apps.config import config, Theme
from bson import ObjectId
from flask import render_template, url_for, request
from flask_login import login_required, current_user
from werkzeug.utils import redirect

@people.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return redirect(url_for('people.posts', id = current_user.id))

# ********************************************************************************************************
@people.route('/<id>', methods=['GET', 'POST'])
def posts(id):
    view_data = get_user_posts(id)
    return render_template('{}/people/posts.html'.format(Theme.THEME_NAME),  view_data=view_data)

@cache.cached(timeout=config['cache_timeout'].USER_POSTS)
def get_user_posts(id):

    sub = request.args.get('sub')
    sort_f = [('time',-1)]
    if sub == 'hot':
        sort_f = [('praise',-1),('pv',-1)]

    temp_data = {}
    try:
        id = ObjectId(id)
        temp_data['profile'] = mdb_user.user_profile.find_one({"user_id":id})
    except:
        temp_data['profile'] = mdb_user.db.user_profile.find_one_or_404({"user_domain":id})
        id = temp_data['profile']["user_id"]

    user = mdb_user.db.user.find_one({"_id":id})
    filter = {'user_id':id, 'status':1}
    view_data = p_posts(request, filter = filter, sort=sort_f, pre=config['paging'].POST_PER_PAGE)
    view_data = dict(view_data, **temp_data)
    view_data['post_tags'] = post_tags(filter={'user_id':id})

    view_data['title'] = "{}的主页-{}".format(user['username'], config['title'].TITLE)

    return view_data

# ********************************************************************************************************************
def sha_query(id, sub):

    view_data = {}
    # user
    view_data['profile'] = mdb_user.db.user_profile.find_one_or_404({'user_id':ObjectId(id)})
    return view_data

# ********************************************************************************************************************
def sha_query2(user_domain, sub):

    view_data = {}
    # user
    view_data['profile'] = mdb_user.db.user_profile.find_one_or_404({'user_domain':user_domain})
    return view_data

