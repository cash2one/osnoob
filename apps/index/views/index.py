from flask import render_template, g
from apps.blueprint import online

__author__ = 'woo'

# **********************************************************************************************************************
@online.route('/', methods=['GET', 'POST'])
def index():
    view_data = {}
    return render_template('{}/index.html'.format(g.theme_name), view_data = view_data)
