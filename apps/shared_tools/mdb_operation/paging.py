#-*-coding:utf-8-*-
from bson import ObjectId

__author__ = 'woo'
#! /usr/bin/env python
# -*-coding:utf-8-*-
from apps import mdb_user

def mongo_paging(db_con, q={}, field={},pre=12, page_num=1,w=4, h=2 ):

    result = {}
    #
    db =db_con
    img_sum = db.find(q).count()
    if img_sum%pre == 0:
        result['page_cnt'] = img_sum/pre
    else:
        result['page_cnt'] = img_sum/pre + 1

    # 当前页图片信息
    if field:
        datas = db.find(q,field).skip(pre*(page_num-1)).limit(pre)
    else:
        datas = db.find(q).skip(pre*(page_num-1)).limit(pre)

    # mongodb 查询的数据只有使用过一次就会没掉，所以这里用list 先保存起来
    datas_list = []
    for img in datas:
        datas_list.append(img)

    result['datas'] = []
    for i in range(0,h):
        j = i+1
        try:
            result['datas'].append(datas_list[i*w:j*w])
        except:
            result['datas'].append([])

    #上一页　下一页
    if page_num > 1:
        result['l_page'] = page_num - 1
    else:
        result['l_page'] = 1
    result['n_page'] = page_num + 1
    if result['n_page'] > result['page_cnt']:
        result['n_page'] = page_num
    result['page_num'] = page_num

    # 显示页数
    if result['page_cnt'] <= 7:
        result['l_show_num'] = range(1, result['page_num'])
        result['n_show_num'] = range(result['page_num']+1, result['page_cnt']+1)

    elif  result['page_num'] < 4:
        result['l_show_num'] = range(1, result['page_num'])
        result['n_show_num'] = range(result['page_num']+1, result['page_num']+5)
        if result['page_num']+5 < result['page_cnt']:
            result['n_show_num'].append('...')
        result['n_show_num'].append(result['page_cnt'])

    elif  result['page_num'] >= 4 and result['page_num'] <= result['page_cnt']-4:
        result['l_show_num'] = [1, '...', result['page_num']-1]
        result['n_show_num'] = range(result['page_num']+1, result['page_num']+4)
        if result['page_num']+4 < result['page_cnt']:
            result['n_show_num'].append('...')
        result['n_show_num'].append(result['page_cnt'])

    elif  result['page_num'] > result['page_cnt']-4:
        result['l_show_num'] = [1,2,'...',result['page_num']-1]
        result['n_show_num'] = range(result['page_num']+1, result['page_cnt']+1)



    # 当前页面图片总数
    #result['img_sum'] = r['data'].count()
    return result


# ************************************************************************************************************************
def mongo_paging_post(db, q={}, pre=12, page_num=1, sort=[('time',-1)], field=None, is_paging=False):

    result = {}
    #
    img_sum = db.find(q).count()
    if img_sum%pre == 0:
        result['page_cnt'] = img_sum/pre
    else:
        result['page_cnt'] = img_sum/pre + 1

    # 当前信息
    if field:
        datas = db.find(q, field).sort(sort).skip(pre*(page_num-1)).limit(pre)
    else:
        datas = db.find(q).sort(sort).skip(pre*(page_num-1)).limit(pre)

    # mongodb 查询的数据只有使用过一次就会没掉，所以这里用list 先保存起来
    datas_list = []
    n = 0
    for d in datas:
        user = mdb_user.db.user.find_one({"_id":ObjectId(d['user_id'])})
        if user:
            d['username'] = user['username']
        else:
            #游客
            d['user_id'] = -1
        d['_id'] = str(d['_id'])
        d['v_t'] = n
        datas_list.append(d)
        if n:
            n = 0
        else:
            n = 1

    result['datas'] = datas_list

    #上一页　下一页
    result['n_page'] = 0
    if page_num > 1:
        result['l_page'] = page_num - 1
    else:
        result['l_page'] = 1
    result['n_page'] = page_num + 1
    if result['n_page'] > result['page_cnt']:
        result['n_page'] = 0
    result['page_num'] = page_num


    # 显示页数
    if is_paging:
        if result['page_cnt'] <= 7:
            result['l_show_num'] = range(1, result['page_num'])
            result['n_show_num'] = range(result['page_num']+1, result['page_cnt']+1)

        elif  result['page_num'] < 4:
            result['l_show_num'] = range(1, result['page_num'])
            result['n_show_num'] = range(result['page_num']+1, result['page_num']+5)
            if result['page_num']+5 < result['page_cnt']:
                result['n_show_num'].append('...')
            result['n_show_num'].append(result['page_cnt'])

        elif  result['page_num'] >= 4 and result['page_num'] <= result['page_cnt']-4:
            result['l_show_num'] = [1, '...', result['page_num']-1]
            result['n_show_num'] = range(result['page_num']+1, result['page_num']+4)
            if result['page_num']+4 < result['page_cnt']:
                result['n_show_num'].append('...')
            result['n_show_num'].append(result['page_cnt'])

        elif  result['page_num'] > result['page_cnt']-4:
            result['l_show_num'] = [1,2,'...',result['page_num']-1]
            result['n_show_num'] = range(result['page_num']+1, result['page_cnt']+1)



    # 当前页面图片总数
    #result['img_sum'] = r['data'].count()
    return result

# ************************************************************************************************************************
def mongo_paging_comment(db, q={}, pre=12, page_num=1, sort=[('time',-1)]):

    result = {}
    #
    img_sum = db.find(q).count()
    if img_sum%pre == 0:
        result['page_cnt'] = img_sum/pre
    else:
        result['page_cnt'] = img_sum/pre + 1

    # 当前信息
    datas = db.find(q).sort(sort).skip(pre*(page_num-1)).limit(pre)

    result['datas'] = datas

    #上一页　下一页
    result['n_page'] = 0
    if page_num > 1:
        result['l_page'] = page_num - 1
    else:
        result['l_page'] = 1
    result['n_page'] = page_num + 1
    if result['n_page'] > result['page_cnt']:
        result['n_page'] = 0
    result['page_num'] = page_num

    # # 显示页数
    # if result['page_cnt'] <= 7:
    #     result['l_show_num'] = range(1, result['page_num'])
    #     result['n_show_num'] = range(result['page_num']+1, result['page_cnt']+1)
    #
    # elif  result['page_num'] < 4:
    #     result['l_show_num'] = range(1, result['page_num'])
    #     result['n_show_num'] = range(result['page_num']+1, result['page_num']+5)
    #     if result['page_num']+5 < result['page_cnt']:
    #         result['n_show_num'].append('...')
    #     result['n_show_num'].append(result['page_cnt'])
    #
    # elif  result['page_num'] >= 4 and result['page_num'] <= result['page_cnt']-4:
    #     result['l_show_num'] = [1, '...', result['page_num']-1]
    #     result['n_show_num'] = range(result['page_num']+1, result['page_num']+4)
    #     if result['page_num']+4 < result['page_cnt']:
    #         result['n_show_num'].append('...')
    #     result['n_show_num'].append(result['page_cnt'])
    #
    # elif  result['page_num'] > result['page_cnt']-4:
    #     result['l_show_num'] = [1,2,'...',result['page_num']-1]
    #     result['n_show_num'] = range(result['page_num']+1, result['page_cnt']+1)

    # 当前页面图片总数
    #result['img_sum'] = r['data'].count()
    return result


# ************************************************************************************************************************
def mongo_paging_msg(db, q={}, pre=12, page_num=1, sort=[('time',-1)], field={}):

    result = {}
    #
    img_sum = db.find(q).count()
    if img_sum%pre == 0:
        result['page_cnt'] = img_sum/pre
    else:
        result['page_cnt'] = img_sum/pre + 1

    # 当前信息
    datas = db.find(q).sort(sort).skip(pre*(page_num-1)).limit(pre)
    result['datas'] = datas

    #上一页　下一页
    result['n_page'] = 0
    if page_num > 1:
        result['l_page'] = page_num - 1
    else:
        result['l_page'] = 1
    result['n_page'] = page_num + 1
    if result['n_page'] > result['page_cnt']:
        result['n_page'] = 0
    result['page_num'] = page_num
    return result

# ************************************************************************************************************************
def mongo_paging_user(db, q={}, pre=6, page_num=1, sort=[('time',-1)], field=None):

    result = {}
    #
    img_sum = db.find(q).count()
    if img_sum%pre == 0:
        result['page_cnt'] = img_sum/pre
    else:
        result['page_cnt'] = img_sum/pre + 1

    # 当前信息
    if field:
        datas = db.find(q, field).sort(sort).skip(pre*(page_num-1)).limit(pre)
    else:
        datas = db.find(q).sort(sort).skip(pre*(page_num-1)).limit(pre)

    # mongodb 查询的数据只有使用过一次就会没掉，所以这里用list 先保存起来
    result['datas'] = []
    if q:
        for data in datas:
            if not 'pay' in data:
                continue
            for p in data['pay'].keys():
                if not "url" in data['pay'][p] or ("$or" in q and data['pay'][p]['status'] != q['$or'][0]['pay.alipay.status']):
                    data['pay'].pop(p)
            result['datas'].append(data)
    else:
        for data in datas:
            result['datas'].append(data)

    #上一页　下一页
    result['n_page'] = 0
    if page_num > 1:
        result['l_page'] = page_num - 1
    else:
        result['l_page'] = 1
    result['n_page'] = page_num + 1
    if result['n_page'] > result['page_cnt']:
        result['n_page'] = 0
    result['page_num'] = page_num


    # 显示页数
    if result['page_cnt'] <= 7:
        result['l_show_num'] = range(1, result['page_num'])
        result['n_show_num'] = range(result['page_num']+1, result['page_cnt']+1)

    elif  result['page_num'] < 4:
        result['l_show_num'] = range(1, result['page_num'])
        result['n_show_num'] = range(result['page_num']+1, result['page_num']+5)
        if result['page_num']+5 < result['page_cnt']:
            result['n_show_num'].append('...')
        result['n_show_num'].append(result['page_cnt'])

    elif  result['page_num'] >= 4 and result['page_num'] <= result['page_cnt']-4:
        result['l_show_num'] = [1, '...', result['page_num']-1]
        result['n_show_num'] = range(result['page_num']+1, result['page_num']+4)
        if result['page_num']+4 < result['page_cnt']:
            result['n_show_num'].append('...')
        result['n_show_num'].append(result['page_cnt'])

    elif  result['page_num'] > result['page_cnt']-4:
        result['l_show_num'] = [1,2,'...',result['page_num']-1]
        result['n_show_num'] = range(result['page_num']+1, result['page_cnt']+1)

    # 当前页面图片总数
    #result['img_sum'] = r['data'].count()
    return result