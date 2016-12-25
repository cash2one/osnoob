#-*-coding:utf-8-*-
from apps import cache, mdb_user
from apps.blueprint import people
from apps.post.process.post import p_posts, post_tags
from apps.config import config
from bson import ObjectId
from flask import render_template, url_for, request
from flask_login import login_required, current_user
from werkzeug.utils import redirect

@people.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return redirect(url_for('people.user', id = current_user.id))

@people.route('/<id>', methods=['GET', 'POST'])
def user(id):

    up = mdb_user.db.user_profile.find_one({'user_id':id})
    if up:
        if up['user_id'] == up['user_domain']:
            prf_id = mdb_user.db.user_profile.find_one_or_404({'user_id':id})['_id']
            prf_id = "account_{}".format(str(prf_id))
            return redirect(url_for('people.posts', prf_id = prf_id))
        else:
            return redirect(url_for('people.posts', prf_id = up['user_domain']))
    else:
        up = mdb_user.db.user_profile.find_one_or_404({'user_domain':id})
        return redirect(url_for('people.posts', prf_id = up['user_domain']))

# ********************************************************************************************************
@people.route('/<prf_id>', methods=['GET', 'POST'])
def posts(prf_id):
    view_data = get_user_posts(prf_id)
    return render_template('people/posts.html',  view_data=view_data)

@cache.cached(timeout=config['cache_timeout'].USER_POSTS)
def get_user_posts(prf_id):

    sub = request.args.get('sub')
    sort_f = [('time',-1)]
    if sub == 'hot':
        sort_f = [('praise',-1),('pv',-1)]
    if "account_" in prf_id:
        temp_data = sha_query(prf_id.replace("account_",""), sub)
    else:
        temp_data = sha_query2(prf_id, sub)

    filter = {'user_id':temp_data['profile']['user_id'], 'status':1}
    view_data = p_posts(request, filter = filter, sort=sort_f, pre=config['paging'].POST_PER_PAGE)
    view_data = dict(view_data, **temp_data)
    view_data['post_tags'] = post_tags(filter={'user_id':temp_data['profile']['user_id']})

    view_data['title'] = "{}的主页-{}".format(temp_data['profile']['username'], config['title'].TITLE)

    return view_data

# ********************************************************************************************************************
def sha_query(prf_id, sub):

    view_data = {}
    # user
    view_data['profile'] = mdb_user.db.user_profile.find_one_or_404({'_id':ObjectId(prf_id)})
    return view_data

# ********************************************************************************************************************
def sha_query2(user_domain, sub):

    view_data = {}
    # user
    view_data['profile'] = mdb_user.db.user_profile.find_one_or_404({'user_domain':user_domain})
    return view_data

