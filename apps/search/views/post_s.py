#-*-coding:utf-8-*-
from flask import request, render_template
from flask_login import current_user
import time
from werkzeug.exceptions import abort
from apps import config, mdb_sys
from apps.blueprint import online
from apps.post.process.post import p_posts, recommend_posts
from apps.search.process.post_s import post_search

__author__ = 'woo'

# ******************************************************************************************************
@online.route('/search', methods=['GET', 'POST'])
def on_search():

    if current_user.is_anonymous() and mdb_sys.db.search_log.find_one({'ip':request.remote_addr, 'time':{'$gt':time.time()-10}}):
        view_data = {}
        view_data['flash'] = {'msg':'未登录用户10秒内只能搜索１次[防机器人]', 'type':'w'}
        view_data['all_page'] = []
        view_data['page_cnt'] = 0
        view_data['post_cnt'] = 0
    else:
        view_data = post_search()
        if current_user.is_anonymous():
            r = mdb_sys.db.search_log.update({'ip':request.remote_addr}, {'$set':{'time':time.time()}},True)
        if not view_data['page_cnt']:
            view_data['flash'] = {'msg':'没有相关内容', 'type':'s'}
        else:
            view_data['flash'] = {'msg':'', 'type':'s'}

    #推荐post
    sort_f = [('praise',-1),('pv',-1)]
    view_data['recommend'] = recommend_posts(sort=sort_f)
    view_data['title'] = "站内搜索-{}".format(config['title'].TITLE)
    view_data['s'] = request.args.get('s',"")
    return render_template('search/posts.html',  view_data=view_data)

# ******************************************************************************************************
@online.route('/sitemap', methods=['GET', 'POST'])
def site_map():

    is_paging = True
    view_data = p_posts(request,pre=20,is_paging=is_paging)
    view_data['post_cnt'] = len(view_data['posts'])
    view_data['title'] = "网站地图-{}".format(config['title'].TITLE)
    if not view_data['post_cnt']:
        abort(404)
    return render_template('search/site_post_map.html',  view_data=view_data)
