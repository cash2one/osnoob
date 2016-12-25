#-*-coding:utf-8-*-
from random import randint
from flask import flash, request, url_for
from flask_login import current_user
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from apps import mdb_user, cache, mdb_cont, mdb_sys
from apps.config import config
from apps.online.process.user import p_user
from apps.post.process.find import find_sort
from apps.shared_tools.image.image_up import img_del
from bs4 import BeautifulSoup
from bson import ObjectId
# ---------------------------------------------------------------------------------------------------------------------
# 文章列表查询
from apps.shared_tools.mdb_operation.paging import mongo_paging_post
from apps.shared_tools.region.osn_format import request_path


def p_posts(request, filter={'status':1, 'subject':{'$ne':'sys'}}, sort=[('time',-1)], field={'body':0}, pre=config['paging'].POST_PER_PAGE_HOME,is_paging=False):


    t_filter = filter.copy()
    t_filter['field'] = field
    t_filter['pre'] = pre
    request_path(t_filter)
    if "user_id" in filter:
         view_data = get_user_p_posts(filter, sort, field, pre,is_paging)
    else:
        view_data = get_p_posts(filter, sort, field, pre,is_paging)
    return view_data

@cache.cached(timeout=config['cache_timeout'].POSTS)
def get_p_posts(filter, sort, field, pre,is_paging):
    view_data = {}
    # page num
    page_num = request.args.get('page',1)
    if not str(page_num).strip():
        page_num = 1
    else:
        page_num = int(page_num)
    if page_num<=0:
        abort(404)
    # 查询
    r = mongo_paging_post(mdb_cont.db.posts, filter , pre=pre,
                          page_num=page_num, sort=sort, field=field,is_paging=is_paging)
    view_data['posts'] = r['datas']
    view_data['n_page'] = r['n_page']
    # nav

    view_data['page_cnt'] =  r['page_cnt']
    view_data['page_num'] =  page_num
    if is_paging:
        view_data['l_page'] = r['l_page']
        view_data['n_page'] = r['n_page']
        view_data['l_show_num'] = r['l_show_num']
        view_data['n_show_num'] = r['n_show_num']
        # all page
        if r['n_show_num']:
            view_data['all_page'] = range(1,r['n_show_num'][-1]+1)
        elif r['l_show_num']:
            view_data['all_page'] = range(1,r['l_show_num'][-1]+1)
        else:
            view_data['all_page'] = []
        if not page_num in view_data['all_page']:
            view_data['all_page'].append(page_num)
            view_data['all_page'].sort()
    return view_data

@cache.cached(timeout=config['cache_timeout'].USER_POSTS)
def get_user_p_posts(filter, sort, field, pre,is_paging):
    view_data = {}
    # page num
    page_num = request.args.get('page',1)
    if not str(page_num).strip():
        page_num = 1
    else:
        page_num = int(page_num)
    if page_num<=0:
        abort(404)
    # 查询
    r = mongo_paging_post(mdb_cont.db.posts, filter , pre=pre,
                          page_num=page_num, sort=sort, field=field,is_paging=is_paging)
    view_data['posts'] = r['datas']
    view_data['n_page'] = r['n_page']
    # nav
    view_data['page_cnt'] =  r['page_cnt']
    view_data['page_num'] =  page_num
    if is_paging:
        view_data['l_page'] = r['l_page']
        view_data['n_page'] = r['n_page']
        view_data['l_show_num'] = r['l_show_num']
        view_data['n_show_num'] = r['n_show_num']

        # all page
        if r['n_show_num']:
            view_data['all_page'] = range(1,r['n_show_num'][-1]+1)
        elif r['l_show_num']:
            view_data['all_page'] = range(1,r['l_show_num'][-1]+1)
        else:
            view_data['all_page'] = []
        if not page_num in view_data['all_page']:
            view_data['all_page'].append(page_num)
            view_data['all_page'].sort()
    return view_data
# ----------------------------------------------------------------------------------------------------------------------
# 推荐文章查询
def recommend_posts(sort = [('time',-1)], filter={'status':1, 'subject':{'$ne':'sys'}}, field={'body':0}):

    request_path(filter)
    recommend = get_recommend_posts(sort,filter ,field)
    return recommend

@cache.cached(timeout=config['cache_timeout'].POST)
def get_recommend_posts(sort,filter,field):

    recommend = find_sort(db=mdb_cont.db.posts, sort=sort, limit=7,
                                        field=field, filter=filter)
    return list(recommend)


# ----------------------------------------------------------------------------------------------------------------------
# 文章类型查询
def post_types(filter ={'$and':[{'subject':{'$ne':'sys'}},{'subject':{'$ne':'region'}}]}):

    # 类型
    _types = mdb_cont.db.post_type.find(filter)
    _post_types = []
    for pt in _types:
        _post_types.extend(pt['type'])
    return _post_types

# ----------------------------------------------------------------------------------------------------------------------
# 文章标签查询
def post_tags(filter = {'user_id':0}):
    # 标签
    request_path(filter)
    _post_tags = get_post_tags(filter)
    return _post_tags

@cache.cached(timeout=config['cache_timeout'].POST_TYPE)
def get_post_tags(filter):
    _post_tags = mdb_cont.db.tag.find_one(filter)
    if _post_tags:
        _post_tags = _post_tags['tag']
    else:
        _post_tags = []
    return _post_tags


# ----------------------------------------------------------------------------------------------------------------------
# 文章标签查询
def new_comments(sort=[('time',-1)], filter = {'status':1,'$or':[{'reply':{'$exists':False}},{'reply':None},{'reply':False}]}):

    request_path(filter)
    _data = get_new_comments(sort, filter)
    return _data

@cache.cached(timeout=config['cache_timeout'].POSTS)
def get_new_comments(sort, filter):

    _new_comments = []
    new_commen_t = find_sort(db=mdb_cont.db.post_comment, sort=sort, limit=5,
                                       filter=filter)
    avatar_l = len(config['user'].AVATAR_URL)
    for c in new_commen_t:
        avatar_url = config['user'].AVATAR_URL[randint(0,avatar_l-1)]
        if not c['user_id']:
            c['avatar_url'] = avatar_url
        else:
            c['avatar_url'] = mdb_user.db.user_profile.find_one({'user_id':c['user_id']}, {'avatar_url':1})['avatar_url']
        _new_comments.append(c)

    return list(_new_comments)

# ----------------------------------------------------------------------------------------------------------------------
#单篇查询
def post_id(args):
    pass


def p_post(filter={'status':1}):
    #request_path(filter)
    view_data = get_p_post(filter)
    return view_data

@cache.cached(timeout=config['cache_timeout'].POST)
def get_p_post(filter):
    view_data = {}
    view_data['post'] = mdb_cont.db.posts.find_one(filter)
    if not view_data['post']:
        if "_id" in filter:
            return {'redirect':url_for('post.preview', post_id=filter['_id'])}
        else:
            return {'redirect':404}
    view_data['post']['_id'] = str(view_data['post']['_id'])
    view_data['profile'] = p_user(view_data['post']['user_id'])
    view_data['post']['username'] = view_data['profile']['username']
    return view_data

# ---------------------------------------------------------------------------------------------------------------------
#浏览量添加
def p_post_pv_1(pid, ua_id):

    _post = mdb_cont.db.posts.find_one({'_id':ObjectId(pid)},{'pv_id':1})
    if ua_id in _post['pv_id'] and ua_id:
        pass
    elif not ua_id:
        mdb_cont.db.posts.update({'_id':ObjectId(pid)}, {"$inc":{"pv":1}})
        return 1
    else:
        mdb_cont.db.posts.update({'_id':ObjectId(pid)}, {'$addToSet':{'pv_id':ua_id},"$inc":{"pv":1}})
        return 1
    return 0


# ------------------------------------------------------------------------------------------------------------------------
# def p_post_add(subject, issue, draft, title, s_type, body, tag_list):
#
#     '''
#     status:
#     0:草稿
#     １:发布
#     ２：待审核
#     ３：审核未通过
#     ４：已删除
#     ５：自动审核通过
#     :return:
#     '''

# ---------------------------------------------------------------------------------------------------------------------
def post_img(str, type):
    soup = BeautifulSoup(str,"lxml")
    imgs = soup.img
    if not imgs:
        url = {'key':'post-{}_default.png'.format(type), 'buckey':'image', 'd':'img'}
    else:
        img_url = imgs['src']
        key = img_url.rsplit('/', 1)[-1]
        url = {'key':key, 'bucket':config['upload'].IMG_B, 'd':'img'}
    return url

# --------------------------------------------------------------------------------------------------------------------
def post_img_statis(str, post_id):

    soup = BeautifulSoup(str,"lxml")
    imgs = soup.findAll("img")
    if imgs:
        p_urls = []
        for img in imgs:
            img_url = img['src']
            p_urls.append(img_url)
        mdb_sys.db.edit_img_log.insert({'user_id':current_user.id, 'case_id':post_id, 'urls':p_urls})
    return 0

# ---------------------------------------------------------------------------------------------------------------------
def edit_img_log_claer(str, post_id=None):

    soup = BeautifulSoup(str,'lxml')
    imgs = soup.findAll("img")
    log = mdb_sys.db.edit_img_log.find_one({'user_id':current_user.id, '$or':[{'case_id':0}, {'case_id':{'$exists': False}}]})
    case_log = {}
    if post_id:
        case_log = mdb_sys.db.edit_img_log.find_one({'user_id':current_user.id, 'case_id':ObjectId(post_id)})
    if log:
        p_urls = []
        for img in imgs:
            img_url = img['src']
            p_urls.append(img_url)

            img['class'] = "img-post-ud"
            img['alt'] = "文章图片"
            img['data-tag'] = "sharePhoto"
            del img['title']

        # user add post img log ------------------------------------------------------------
        log_urls = log['urls'][:]
        for l_url in log_urls:
            if not l_url in p_urls:
                # 如过这张图片不在文章里面，这删除
                key = l_url.rsplit('/', 1)[-1]
                img_del({'bucket':config['upload'].IMG_B,'key':key})
            log['urls'].remove(l_url)
        mdb_sys.db.edit_img_log.update({'user_id':current_user.id}, {'$set':{'urls':log['urls']}})

        # user edit post img log -----------------------------------------------------------
        if case_log:
            case_urls = case_log['urls'][:]
            for l_url in case_urls:
                if not l_url in p_urls:
                    # 如过这张图片不在文章里面，这删除
                    key = l_url.rsplit('/', 1)[-1]
                    img_del({'bucket':config['upload'].IMG_B,'key':key})
            # remove case img log
            mdb_sys.db.edit_img_log.remove({'user_id':current_user.id, 'case_id':ObjectId(post_id)})

    # a
    tag_a = soup.findAll("a")
    for a in tag_a:
        a['rel'] = "nofollow"
    soup = post_filter(soup)
    return unicode(soup)

# ---------------------------------------------------------------------------------------------------------------------
def sys_edit_img_log_claer(str, post_id=None, post_title = None):

    soup = BeautifulSoup(str,'lxml')
    imgs = soup.findAll("img")
    log = mdb_sys.db.edit_img_log.find_one({'user_id':current_user.id, '$or':[{'case_id':0}, {'case_id':{'$exists': False}}]})
    case_log = {}
    if post_id:
        case_log = mdb_sys.db.edit_img_log.find_one({'user_id':current_user.id, 'case_id':ObjectId(post_id)})
    if log:
        p_urls = []
        for img in imgs:
            img_url = img['src']
            p_urls.append(img_url)

            img['class'] = "img-post-ud"
            img['alt'] = "文章图片"
            img['data-tag'] = "sharePhoto"
            del img['title']

        # user add post img log ------------------------------------------------------------
        log_urls = log['urls'][:]
        for l_url in log_urls:
            if not l_url in p_urls:
                # 如过这张图片不在文章里面，这删除
                key = l_url.rsplit('/', 1)[-1]
                img_del({'bucket':config['upload'].IMG_B,'key':key})
            log['urls'].remove(l_url)
        mdb_sys.db.edit_img_log.update({'user_id':current_user.id}, {'$set':{'urls':log['urls']}})

        # user edit post img log -----------------------------------------------------------
        if case_log:
            case_urls = case_log['urls'][:]
            for l_url in case_urls:
                if not l_url in p_urls:
                    # 如过这张图片不在文章里面，这删除
                    key = l_url.rsplit('/', 1)[-1]
                    img_del({'bucket':config['upload'].IMG_B,'key':key})
            # remove case img log
            mdb_sys.db.edit_img_log.remove({'user_id':current_user.id, 'case_id':ObjectId(post_id)})

    # a
    if post_title != u"友情链接":
        tag_a = soup.findAll("a")
        for a in tag_a:
            a['rel'] = "nofollow"
    soup = post_filter(soup)
    return unicode(soup)


# 防止xss
def post_filter(soup):

    # 删除这些标签
    try:
        soup.script.decompose()
    except:
        pass
    try:
        soup.link.decompose()
    except:
        pass
    try:
        soup.meta.decompose()
    except:
        pass
    try:
        ifs = soup.findAll("iframe")
        for ifr in ifs:
            if not "http://music.163.com" in ifr['src'] and not "www.xiami.com" in ifr['src']:
                soup.iframe.decompose()
                flash({'type':'w','msg':u'您插入的非法代码已被过滤！'})
                break
    except:
        pass

    return soup
