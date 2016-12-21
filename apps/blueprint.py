from flask import Blueprint


__author__ = 'woo'

# create blueprint
#admin

admin = Blueprint('admin', __name__, template_folder="themes")
# front
api = Blueprint('api', __name__)

base = Blueprint('base', __name__, template_folder="themes")

online = Blueprint('online', __name__, template_folder="themes")

people = Blueprint('people', __name__, template_folder="themes")

comments = Blueprint('comments', __name__, template_folder="themes")

post = Blueprint('post', __name__, template_folder="themes")

media = Blueprint('media', __name__, template_folder="themes")

audit = Blueprint('audit', __name__, template_folder="themes")

pay = Blueprint('pay', __name__, template_folder="themes")

#admin
# from apps.admin.views import user, index
# from apps.multimedia.views import image
# from apps.audit.views import  rule
# from apps.pay.views import  pays

# view
from apps.index.views import index
from apps.online.views import user

#from apps.online.views import user, index, msg
# from apps.people.views import index
# from apps.post.views import posts, show, management, type_tag
# from apps.msg.views import msgs
# from apps.search.views import post_s

# api
from apps.online.apis import user, oauth_login
# from apps.post.apis import post_api
# from apps.comment.apis import comment
# from apps.online.apis import vercode, user, pageview
# from  apps.online.process import oauth_login
# from apps.msg.apis import msg_api
# from apps.search.apis import post_s


