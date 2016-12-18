# -*-coding:utf-8-*-
import time
from apps import mail, app
from apps.shared_tools.decorator.decorators import async

__author__ = 'woo'
@async
def send_async_email(app, msg, db):
    with app.app_context():
        try:
            r = mail.send(msg)
            if not r:
                status = 0
        except:
            status = -1

    log = {
        'status':status,
        'subject':msg.subject,
        'from':msg.sender,
        'to':list(msg.send_to),
        'date':msg.date,
        'body':msg.body,
        'html':msg.html,
        'msgid':msg.msgId,
        'time':time.time()
    }
    db.email_log.insert(log)

def send_email(db, msg):
    send_async_email(app, msg, db)
