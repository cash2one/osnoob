__author__ = 'woo'


def find_sort(db, sort, limit = 5, filter = {}, field=None):

    if field:
        datas = db.find(filter, field).sort(sort).limit(limit)
    else:
        datas = db.find(filter).sort(sort).limit(limit)
    return datas
