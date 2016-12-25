#-*-coding:utf-8-*-
from flask import jsonify
from apps.blueprint import api
from apps.search.process.post_s import post_search

__author__ = 'woo'
# ---------------------------------------------------------------------------------------------------------------
@api.route('/s/posts', methods=['GET'])
def s_posts():
    _data = post_search()
    return jsonify(_data)
