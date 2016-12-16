#-*-coding:utf-8-*-
from flask import request, jsonify
import time
from apps import mdb_sys
from apps.blueprint import api

__author__ = 'woo'

# --------------------------------------------------------------------------------------------------------
@api.route('/pageview/add', methods=['POST'])
def page_view_add():

    url = request.form['url']

    mdb_sys.db.page_view_log.update({'url':url}, {'$inc':{'pv':1},"$set":{'time':time.time()}}, True)
    return jsonify({})