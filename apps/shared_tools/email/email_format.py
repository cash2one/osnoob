import re

__author__ = 'woo'

def ver_email(email):

    return re.search(r"^[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$",email.strip())
