#-*-coding:utf-8-*-
import urllib
from uuid import uuid1
from apps.config import config
import os
from flask import flash
from apps import qn as q
from qiniu import put_file, etag,  BucketManager

__author__ = 'woo'

# **********************************************************************************************************************
# 图片上传
def img_up(uploaded_files, bucket, dir_path = "media_temp", new_name=None):
    '''

    :param uploaded_files:
    :param dir_path:
    :param new_name:
    :return:img url
    '''
    domain = bucket['domain']
    bucket_name = bucket['b']
    project = bucket['project']
    result = {'url':1}
    if not uploaded_files:
        result['url'] = 1
        return result
    for file in uploaded_files:
        if file:
            if not allowed_file(file.filename):
                flash({'type':'e', 'msg':u'图片格式不对！'})
            # 如果自定义名字
            if new_name:
                filename = '{}-{}.{}'.format(project, new_name, file.filename.rsplit('.', 1)[1].lower())
                temp_filename = '{}_{}.{}'.format(bucket_name, new_name, file.filename.rsplit('.', 1)[1].lower())
            else:
                filename = '{}-{}.{}'.format(project, uuid1(),file.filename.rsplit('.', 1)[1].lower())
                temp_filename = '{}_{}.{}'.format(bucket_name, uuid1(),file.filename.rsplit('.', 1)[1].lower())

            # 本地服务器------------------------------------------------------------------
            # 图片保存的绝对路径
            save_dir = os.path.join("{}/{}/".format(config['upload'].HOST, dir_path))
            # 保存图片
            r = file.save(os.path.join(save_dir, temp_filename))
            # 修改图片
            if not r:
                localurl = os.path.join(dir_path, temp_filename)
                localpath = os.path.join("{}/{}".format(config['upload'].HOST, localurl))
                # 七牛---------------------------------------------------------------------
                result['url'] = qiniu_save(bucket_name, filename, localpath, domain)
                # 删除本地服务武器临时文件
                local_img_del(localurl)

            else:
                result['url'] = -1

        else:
            result['url'] = -1
    return result


# ----------------------------------------------------------------------------------------------------------------------
def qiniu_save(bucket_name, key, localfile, domain):


    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_file(token, key, localfile)
    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)
    #有两种方式构造base_url的形式
    url = {'bucket':bucket_name,'d':domain, 'key':key}
    return url


# **********************************************************************************************************************
# 图片格式验证
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config['upload'].ALLOWED_EXTENSIONS

# **********************************************************************************************************************
def local_img_del(url):
    try:
        os.remove(os.path.join("{}/{}".format(config['upload'].HOST, url)))
    except:
        pass

# **********************************************************************************************************************
def img_del(url):

    #初始化BucketManager
    bucket = BucketManager(q)
    #删除bucket_name 中的文件 key
    ret, info = bucket.delete(url['bucket'], url['key'])
    try:
        assert ret == {}
    except:
        print "error-del"
        return -1
    return 0

# ---------------------------------------------------------------------------------------------------------------------
def img_rename(url, new_name):

    # path = url.rsplit('/', 1)[0]
    # ft = url.rsplit('.', 1)[1]
    # new_url = "{}/{}.{}".format(path, new_name, ft)
    # os.rename("{}/{}".format(config['upload'].HOST, url), "{}/{}".format(config['upload'].HOST, new_url))
    # return new_url

    #初始化BucketManager
    bucket = BucketManager(q)
    project = url['key'].rsplit('-',1)[0]
    filename = '{}-{}.{}'.format(project, new_name, url['key'].rsplit('.', 1)[1])
    ret, info = bucket.move(url['bucket'], url['key'], url['bucket'],filename )

    return {'bucket':url['bucket'],'d':url['d'], 'key':filename}

# 远程图片----------------------------------------------------------------------------------------------------------------
def img_fetch(url, bucket, dir_path = "media_temp", new_name=None):

    result = {'url':1}
    domain = bucket['domain']
    bucket_name = bucket['b']
    project = bucket['project']
    # 如果自定义名字
    if new_name:
        filename = '{}-{}.{}'.format(project, new_name, "jpg")
        temp_filename = '{}_{}.{}'.format(bucket_name, new_name, "jpg")
    else:
        filename = '{}-{}.{}'.format(project, uuid1(), "jpg")
        temp_filename = '{}_{}.{}'.format(bucket_name, uuid1(), "jpg")

    # 本地服务器------------------------------------------------------------------
    # 图片保存的绝对路径
    save_dir = os.path.join("{}/{}/".format(config['upload'].HOST, dir_path))

    # 下载图片
    urllib.urlretrieve(url, "{}{}".format(save_dir,temp_filename))
    # 修改图片
    localurl = os.path.join(dir_path, temp_filename)
    localpath = os.path.join("{}/{}".format(config['upload'].HOST, localurl))
    # 七牛---------------------------------------------------------------------
    result['url'] = qiniu_save(bucket_name, filename, localpath, domain)
    # 删除本地服务武器临时文件
    local_img_del(localurl)
    return result

