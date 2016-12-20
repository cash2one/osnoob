#!/usr/bin/env python
#-*-coding:utf-8-*-
from flask import render_template
from apps.blueprint import base
from apps.config import config

__author__ = 'woo'

# **********************************************************************************************************************
@base.route('/', methods=['GET', 'POST'])
def index():
    view_data = {"title":u"Osnoob-Open source CMS"}
    return render_template('{}/index.html'.format(config['theme'].THEME_NAME), view_data = view_data)
