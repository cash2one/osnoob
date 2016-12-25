#-*-coding:utf-8-*-
from apps import mdb_sys, cache
from apps.shared_tool.my_format import request_path

__author__ = 'woo'

# ----------------------------------------------------------------------------------------------------------------------
# 图片查询
def find_imgs(sort = [('time',-1)], filter={}):

    request_path(filter)
    imgs = get_find_imgs(filter)
    return imgs

@cache.cached()
def get_find_imgs(filter):

    imgs = mdb_sys.db.img.find(filter)
    return list(imgs)