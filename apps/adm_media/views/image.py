#-*-coding:utf-8-*-
from apps import config as app_config, mdb_cont
import json,time
from apps.config import Permission, Theme
from apps.adm_media.process.uploader import Uploader
import os
from apps import mdb_sys
from apps.blueprint import media, online, base
from apps.adm_media.forms.image import EditImgForm, ImgForm, ImgDelForm
from apps.shared_tools.image.image_up import img_up, img_del, img_rename, qiniu_save, local_img_del
from bson import ObjectId
from flask import request, flash, render_template, redirect, url_for, make_response
from flask_login import login_required, current_user
import re
from werkzeug.exceptions import abort
from apps.shared_tools.decorator.decorators import permission_required

__author__ = 'woo'

# *********************************************************************************************************************
# 图片管理
@media.route('/image/add', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def add_img():

    view_data = {'title':'添加图片'}
    form = EditImgForm()
    if form.submit.data:
        if not form.name.data.strip():
            flash({'type':'w', 'msg':'名字不能为空！'})
            return render_template('{}/media/image/add_img.html'.format(Theme.ADM_THEME_NAME), form=form, view_data=view_data)
        uploaded_files = request.files.getlist("img")
        bucket_name = {'b':app_config['upload'].IMG_B, 'domain':'img', 'project':form.project.data}
        r = img_up(uploaded_files, bucket_name, new_name=form.name.data.strip())
        if r['url'] != -1 and r['url'] != 1:
            img_profile = {
                'url':r['url'],
                'type':form.project.data ,
                'time':time.time(),
                'name':form.name.data.strip(),
                'showname':form.showname.data.strip(),
                'info':form.info.data,
                'link':form.link.data.strip()
            }
            mdb_sys.db.img.insert(img_profile)
            flash({'msg':'成功.','type':'s'})
        else:
            flash({'msg':'图片上传失败！','type':'e'})
        return redirect(url_for('media.image', project=form.project.data))

    return render_template('{}/media/image/add_img.html'.format(Theme.ADM_THEME_NAME), form=form, view_data=view_data)

# *********************************************************************************************************************
# 图片编辑
@media.route('/image/edit/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def edit_img(id):

    view_data = {'op_type':'edit', 'title':'编辑图片信息'}
    form = EditImgForm()
    view_data['img'] = mdb_sys.db.img.find_one_or_404({'_id':ObjectId(id)})
    if form.submit.data:
        if not form.name.data.strip():
            flash({'type':'w', 'msg':'名字不能为空！'})
        else:
            uploaded_files = request.files.getlist("img")
            bucket_name = {'b':app_config['upload'].IMG_B, 'domain':'img', 'project':form.project.data}

            if uploaded_files[0]:
                img_del(view_data['img']['url'])
            r = img_up(uploaded_files, bucket_name, new_name=form.name.data.strip())
            if r['url'] != -1 and r['url'] != 1:
                img_profile = {
                    'url':r['url'],
                    'time':time.time(),
                    'name':form.name.data.strip(),
                    'showname':form.showname.data.strip(),
                    'info':form.info.data,
                    'link':form.link.data.strip()
                }
                mdb_sys.db.img.update({'_id':ObjectId(id)}, {'$set':img_profile})
                flash({'msg':'成功.','type':'s'})

            else:
                url = view_data['img']['url']
                if form.name.data.strip() != view_data['img']['name']:
                    new_url = img_rename(url, form.name.data.strip())
                else:
                    new_url = url
                img_profile = {
                    'url':new_url,
                    'time':time.time(),
                    'name':form.name.data.strip(),
                    'showname':form.showname.data.strip(),
                    'info':form.info.data,
                    'link':form.link.data.strip()
                }
                mdb_sys.db.img.update({'_id':ObjectId(id)}, {'$set':img_profile})

            return redirect(url_for('media.image', project = view_data['img']['type']))


    form.name.data = view_data['img']['name']
    form.project.data = view_data['img']['type']
    form.showname.data = view_data['img']['showname']
    form.info.data = view_data['img']['info']
    form.link.data = view_data['img']['link']
    return render_template('{}/media/image/add_img.html'.format(Theme.ADM_THEME_NAME), form=form, view_data=view_data)

# *********************************************************************************************************************
@media.route('/image', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def image():

    view_data = {'title':'图片管理'}
    form = ImgForm()
    form_del = ImgDelForm()
    project = request.args.get('project','adv')
    view_data['imgs'] = mdb_sys.db.img.find({'type':project})
    form.project.data = view_data['project'] = project
    return render_template('{}/media/image/img.html'.format(Theme.ADM_THEME_NAME),
                           view_data=view_data, form=form, form_del=form_del)


# *********************************************************************************************************************
@media.route('/delete-img', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def delete_img():

    form_del = ImgDelForm()
    if form_del.submit.data:
        url_list = request.form.getlist("boolean")
        id_len = len(url_list)
        op_type = form_del.op_type.data
        if op_type=='delete':
            for url in url_list:
                url = eval(url)
                if url == 'y':
                    id_len -= 1
                    continue
                mdb_sys.db.img.remove({'url':url})
                img_del(url)
            flash({'msg':u'删除了{}张图片'.format(id_len), 'type':'s'})

        return redirect(url_for('media.image', project=form_del.q.data))
    abort(404)


# ------------------------------------------------------------------------------------------------------------------------------
@base.route('/upload/', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def upload():

    """UEditor文件上传接口

    config 配置文件
    result 返回结果
    """

    mimetype = 'application/json'
    result = {}
    action = request.args.get('action')
    local_path = os.path.join(app_config['upload'].HOST)
    # 解析JSON格式的配置文件
    with open(os.path.join('{}/{}'.format(app_config['upload'].HOST, 'media_temp/config.json'))) as fp:
        try:
            # 删除 `/**/` 之间的注释
            CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
        except:
            CONFIG = {}

    if action == 'config':
        # 初始化时，返回配置文件给客户端
        result = CONFIG

    elif action in ('uploadimage', 'uploadfile', 'uploadvideo'):
        # 图片、文件、视频上传
        if action == 'uploadimage':
            fieldName = CONFIG.get('imageFieldName')
            config = {
                "pathFormat": CONFIG['imagePathFormat'],
                "maxSize": CONFIG['imageMaxSize'],
                "allowFiles": CONFIG['imageAllowFiles']
            }
        elif action == 'uploadvideo':
            fieldName = CONFIG.get('videoFieldName')
            config = {
                "pathFormat": CONFIG['videoPathFormat'],
                "maxSize": CONFIG['videoMaxSize'],
                "allowFiles": CONFIG['videoAllowFiles']
            }
        else:
            fieldName = CONFIG.get('fileFieldName')
            config = {
                "pathFormat": CONFIG['filePathFormat'],
                "maxSize": CONFIG['fileMaxSize'],
                "allowFiles": CONFIG['fileAllowFiles']
            }
        if fieldName in request.files:
            field = request.files[fieldName]
            uploader = Uploader(field, config, local_path)
            result = uploader.getFileInfo()

            #　----------------------上传到图片服务器端-------------------------------------------
            result = up_to_qn(result)
        else:
            result['state'] = '上传接口出错'

    elif action in ('uploadscrawl'):
        # 涂鸦上传
        fieldName = CONFIG.get('scrawlFieldName')
        config = {
            "pathFormat": CONFIG.get('scrawlPathFormat'),
            "maxSize": CONFIG.get('scrawlMaxSize'),
            "allowFiles": CONFIG.get('scrawlAllowFiles'),
            "oriName": "scrawl.png"
        }
        if fieldName in request.form:
            field = request.form[fieldName]
            uploader = Uploader(field, config, local_path, 'base64')
            result = uploader.getFileInfo()
            #　----------------------上传到图片服务器端-------------------------------------------
            result = up_to_qn(result)
        else:
            result['state'] = '上传接口出错'

    elif action in ('catchimage'):
        config = {
            "pathFormat": CONFIG['catcherPathFormat'],
            "maxSize": CONFIG['catcherMaxSize'],
            "allowFiles": CONFIG['catcherAllowFiles'],
            "oriName": "remote.png"
        }
        fieldName = CONFIG['catcherFieldName']

        if fieldName in request.form:
            # 这里比较奇怪，远程抓图提交的表单名称不是这个
            source = []
        elif '%s[]' % fieldName in request.form:
            # 而是这个
            source = request.form.getlist('%s[]' % fieldName)

        _list = []
        for imgurl in source:
            uploader = Uploader(imgurl, config, local_path, 'remote')
            info = uploader.getFileInfo()
            _list.append({
                'state': info['state'],
                'url': info['url'],
                'original': info['original'],
                'source': imgurl,
            })

        result['state'] = 'SUCCESS' if len(_list) > 0 else 'ERROR'
        result['list'] = _list
        for img in result['list']:
            img = up_to_qn(img)
        print result

    else:
        result['state'] = '请求地址出错'

    result = json.dumps(result)

    if 'callback' in request.args:
        callback = request.args.get('callback')
        if re.match(r'^[\w_]+$', callback):
            result = '%s(%s)' % (callback, result)
            mimetype = 'application/javascript'
        else:
            result = json.dumps({'state': 'callback参数不合法'})

    res = make_response(result)
    res.mimetype = mimetype
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
    return res


# ------------------------------------------------------------------------------------------------------
def up_to_qn(result):
    #　----------------------上传到图片服务器端-------------------------------------------
    temp_filename = result['url'].rsplit('/', 1)[1]
    dir_path = "media_temp"
    localurl = os.path.join(dir_path, temp_filename)
    localpath = os.path.join("{}/{}".format(app_config['upload'].HOST, localurl))
    bucket = {'b':app_config['upload'].IMG_B, 'domain':'img', 'project':'post'}
    from uuid import uuid1
    filename = '{}-{}.{}'.format(bucket['project'], uuid1(),temp_filename.rsplit('.', 1)[1])
    img_url = qiniu_save(bucket['b'], filename, localpath, bucket['domain'])

    # 返回给编辑器并删除本地
    _url = "http://{}/{}".format(app_config['upload'].IMG_HOST, img_url['key'])
    # 记录 上传的图片
    mdb_cont.db.edit_img_log.update({'user_id':current_user.id}, {"$addToSet":{'urls':_url}},True)
    # if not r['updatedExisting']:
    #     mdb.db.edit_img_log.insert({'user_id':current_user.id, 'urls':[result['url']]})

    result['url'] = _url
    local_img_del(localurl)
    return result