from flask import request

__author__ = 'woo'

class MyRequest():

    def all(self, key=None, d_value=None):
        '''
        all parameter
        :param key: key
        :param d_value: None
        :return:
        '''
        if not key:
            return request.json,request.form,request.values
        elif request.json and key in request.json:
            _value = request.json[key]
        elif key in request.form:
            _value = request.form[key]
        elif key in request.values:
            _value = request.values[key]
        else:
            _value = d_value
        return _value

    def list(self, key=None, d_value=None):
        '''
        all parameter
        :param key: key
        :param d_value: None
        :return:
        '''
        if not key:
            return request.json,request.form,request.values
        elif request.json and key in request.json:
            _value = request.json[key]
        elif key in request.form:
            _value = request.form.getlist(key)
        elif key in request.values:
            _value = request.values.getlist(key)
        else:
            _value = d_value
        return _value


