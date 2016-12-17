from flask import Blueprint


__author__ = 'woo'

# create blueprint
#admin
admin = Blueprint('admin', __name__, template_folder="templates", static_url_path='/static', static_folder='static')
# front
api = Blueprint('api', __name__)

online = Blueprint('online', __name__, template_folder="templates", static_url_path='/static', static_folder='static')

people = Blueprint('people', __name__, template_folder="templates", static_url_path='/static', static_folder='static')

comments = Blueprint('comments', __name__, template_folder="templates", static_url_path='/static', static_folder='static')

post = Blueprint('post', __name__, template_folder="templates", static_url_path='/static', static_folder='static')

media = Blueprint('media', __name__, template_folder="templates", static_url_path='/static', static_folder='static')

audit = Blueprint('audit', __name__, template_folder="templates", static_url_path='/static', static_folder='static')

pay = Blueprint('pay', __name__, template_folder="templates", static_url_path='/static', static_folder='static')

#admin
# from apps.admin.views import user, index
# from apps.multimedia.views import image
# from apps.audit.views import  rule
# from apps.pay.views import  pays

# front
#from apps.online.views import user, index, msg
# from apps.people.views import index
# from apps.post.views import posts, show, management, type_tag
# from apps.msg.views import msgs
# from apps.search.views import post_s

# api
# from apps.post.apis import post_api
# from apps.comment.apis import comment
# from apps.online.apis import vercode, user, pageview
# from  apps.online.process import oauth_login
# from apps.msg.apis import msg_api
# from apps.search.apis import post_s


