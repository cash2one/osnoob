#-*-coding:utf-8-*-
from flask import request, jsonify
from werkzeug.exceptions import abort
from apps import config
from apps.post.process.post import p_posts

__author__ = 'woo'
def post_search():

    user_id = request.args.get('user_id')
    s = request.args.get('s',"").strip()
    if not s:
        return {'post_cnt':0, 'page_cnt':0, 'all_page':[]}
    filter = {"title":{"$regex":".*{}.*".format(s), "$options": 'i'},  'status':1}
    if user_id:
        filter['user_id'] = int(user_id)
        is_paging = False
    else:
        is_paging = True
    _data = p_posts(request, filter=filter, pre=config['paging'].POST_SEARCH,is_paging=is_paging)

    if (_data['page_num'] > _data['page_cnt'] and _data['page_cnt']>0) or _data['page_num'] < 0:
        abort(404)
    _data['post_cnt'] = len(_data['posts'])
    return _data
