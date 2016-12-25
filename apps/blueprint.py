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
from apps.adm_dashboard.views import index
from apps.adm_user.views import user
from apps.adm_media.views import image
from apps.audit.views import  rule
from apps.adm_pay.views import  pays
from apps.adm_type.views import  type_tag
from apps.adm_post.views import management
from apps.adm_comment.views import comment


# view
from apps.index.views import index
from apps.online.views import user

from apps.online.views import user,msg
from apps.people.views import index
from apps.post.views import posts, show

from apps.msg.views import msgs
from apps.search.views import post_s

# api
from apps.online.apis import user, oauth_login
from apps.post.apis import post_api
from apps.comment.apis import comment
from apps.verify.apis import vercode
from apps.msg.apis import msg_api
from apps.search.apis import post_s
from apps.online.apis import oauth_login


