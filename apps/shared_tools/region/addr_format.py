#-*-coding:utf-8-*-
from apps import mdb_sys

__author__ = 'woo'

def addr_f():
    cjson = {}
    _json = []
    s_cnt = 1
    t = mdb_sys.db.content_type.find_one({'subject':"region"})
    if t:
        cjson = t['type']
    for k,v in cjson.items():
        s = {}
        #　省份
        s['text'] = k
        s["id"]= "1{}0000".format(s_cnt)
        s["parentId"]= None
        s["text"]=k
        s["children"] = []
        c_cnt = 1
        for sk,kv in v.items():
            si = {}
            _c_cnt = c_cnt
            if c_cnt < 10:
                _c_cnt = "0{}".format(c_cnt)
            si["id"]="1{}{}00".format(s_cnt,_c_cnt)
            si["parentId"]=None
            si["text"] = sk
            si["children"] = []
            a_cnt = 1
            for q_text in kv:
                _a_cnt = a_cnt
                if a_cnt < 10:
                    _a_cnt = "0{}".format(a_cnt)
                q_id = "1{}{}{}".format(s_cnt,_c_cnt,_a_cnt)
                q = {
                      "id": q_id,
                      "parentId": None,
                      "text": q_text,
                      "children": [],
                      "statNum": 0
                    }
                si["children"].append(q)
                a_cnt += 1
            c_cnt += 1
            s["children"].append(si)
        s_cnt += 1
        _json.append(s)
    return _json