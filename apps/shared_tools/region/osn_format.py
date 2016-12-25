#-*-coding:utf-8-*-
from flask import request

__author__ = 'woo'

def mongo_to_list(d):

    for k,v in d:
        if v == 1:
            pass

def request_path(names):
    _names = "?"
    if type(names) == type([]):
        t_names = names
        t_names.append('page')
        for name in t_names:
            _names = "{}&{}={}".format(_names, name, request.args.get(name,""))
    else:
        t_names = names.copy()
        t_names['page'] = 1
        for name in t_names:
            _names = "{}&{}={}".format(_names, name, request.args.get(name,t_names[name]))


    request.path = "{}/{}".format(request.path, _names)
