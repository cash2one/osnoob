#-*-coding:utf-8-*-
from apps.blueprint import api
from apps.verify.process.email_code import create_email_code, verify_email_code
from apps.verify.process.ver_code import create_code, verify_code
from flask import jsonify, request, flash

__author__ = 'woo'

@api.route('/get-vercode', methods=['GET', 'POST'])
def vercode():

    # 验证码
    _code = create_code()
    return jsonify(_code)

# --------------------------------------------------------------------------------------------------------
@api.route('/get-email-code', methods=['GET', 'POST'])
def email_code():

    email = request.form['email']
    # 验证码
    if email:
        _code = create_email_code(email.strip(), cnt=6)
    else:
        _code = {}
    return jsonify(_code)

# --------------------------------------------------------------------------------------------------------
@api.route('/get-email-code/ps', methods=['POST'])
def ret_ps_email_code():

    _code = {}
    email = request.form['email']
    code = request.form['vercode']
    code_id = request.form['vercode_url']
    # 验证码
    r = verify_code(code_id, code)
    if not r:
        _code['flash'] = {'msg':'图片验证码错误！', 'type':'e'}

    else:
        if email:
            _code = create_email_code(email.strip(), cnt=8)
        else:
            _code = {}
    return jsonify(_code)