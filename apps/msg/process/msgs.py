#*-*coding:utf8*-*
import time
from bson import ObjectId
from apps import mdb_user, mdb_cont
from apps.shared_tools.mdb_operation.paging import mongo_paging_msg

__author__ = 'woo'

# ----------------------------------------------------------------------------------------------------------------------
# 添加消息
def add_msg(msg_str, url, user_id, case_id=None,case_status=1, sub=None, type=None):

    msg = {
        'msg':msg_str,
        'user_id':user_id,
        'sub':sub,
        'type':type,
        'url':url,
        'time':time.time(),
        'case_id':case_id,
        'status':0,
        'case_status':case_status,
    }
    _id= mdb_user.db.msg.insert(msg)
    return _id


# ----------------------------------------------------------------------------------------------------------------------
# 改变消息状态
def sta_msg(id, uid, status=1):
    '''
    0 新消息
    １　已读
    ２　移除
    :param id:
    :param status:
    :return:
    '''
    r = mdb_user.db.msg.update({'_id':ObjectId(id),'user_id':uid}, {'$set':{'status':status}})
    return r

# ----------------------------------------------------------------------------------------------------------------------
def sta_msg_all(uid, status=1):
    '''
    0 新消息
    １　已读
    ２　移除
    :param id:
    :param status:
    :return:
    '''

    r = mdb_user.db.msg.update({'user_id':uid, 'status':0}, {'$set':{'status':status}})
    return r

# ----------------------------------------------------------------------------------------------------------------------
# 删除消息
def del_msg(id):

    r = mdb_user.db.msg.remove({'_id':ObjectId(id)})
    return r

# ----------------------------------------------------------------------------------------------------------------------
def p_msgs(request, filter={'sub':{'$ne':'sys'}, 'status':{'$ne':2}, 'case_status':1}, sort=[('time',-1)], field={}, pre=10):

    view_data = {}
    # page num
    page_num = int(request.args.get('page',1))
    # 查询
    r = mongo_paging_msg(mdb_user.db.msg, filter , pre=pre,
                          page_num=page_num, sort=sort, field=field)
    view_data['msgs'] = []
    for data in r['datas']:
        c = mdb_cont.db.post_comment.find_one({'_id':ObjectId(data['case_id'])})
        if c:
            data['body'] = c['comment']
        data['_id'] = str(data['_id'])
        data['case_id'] = str(data['case_id'])
        view_data['msgs'].append(data)
    view_data['n_page'] = r['n_page']
    return view_data
