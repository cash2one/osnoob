#!/usr/bin/env python
#-*-coding:utf-8-*-
from datetime import datetime
from random import randint
import time
from flask import  request, g
from flask_login import current_user
import os
from apps import config


__author__ = 'woo'

class Config:

    @staticmethod
    def init_app(app):
        pass

# **********************************************************************************************************************
class logger(Config):
    @classmethod
    def init_app(self, app):
        Config.init_app(app)
        # Save the error message
        if not app.debug:
            import logging

            # ----------------------------------------------------------------------------------------------------------
            lf_path = os.path.dirname(__file__)
            logs_path = "{}/../logs".format(lf_path)
            if not os.path.exists(logs_path):
                 os.makedirs(logs_path)

            formatter = logging.Formatter(config['weblogger'].FORMATTER)
            # ----------------------------------------------------------------------------------------------------------
            filename = os.path.abspath("{}/../logs/web_error.log".format(lf_path))
            from logging.handlers import TimedRotatingFileHandler
            # According to the time
            file_handler = TimedRotatingFileHandler(filename, "midnight", 1, 30)
            file_handler.suffix = "%Y-%m-%d"

            # According to the size
            #file_handler = RotatingFileHandler(filename, maxBytes=10*1024*1024, backupCount=5)
            file_handler.setLevel(config['weblogger'].EXCEP_LEVEL)
            file_handler.setFormatter(formatter)
            app.logger.addHandler(file_handler)
            logging.getLogger('err_log').addHandler(file_handler)
            logging.getLogger('err_log').setLevel(config['weblogger'].EXCEP_LEVEL)


            # ----------------------------------------------------------------------------------------------------------
            filename= os.path.abspath("{}/../logs/normal.log".format(lf_path))
            # According to the time
            file_handler = TimedRotatingFileHandler(filename, "midnight", 1, 30)
            file_handler.suffix = "%Y-%m-%d"
            # According to the size
            #file_handler = RotatingFileHandler(filename, maxBytes=10*1024*1024,backupCount=5)
            file_handler.setLevel(config['weblogger'].NORMAL_LEVEL)
            file_handler.setFormatter(formatter)

            logging.getLogger('r_log').addHandler(file_handler)
            logging.getLogger('r_log').setLevel(config['weblogger'].NORMAL_LEVEL)


            # Access to information-------------------------------------------------------------------------------------
            @app.before_request
            def before_request():
                global sys_weblog
                sys_weblog = {}
                sys_weblog['user'] = current_user
                sys_weblog['log'] = {}
                st = datetime.utcnow()

                sys_weblog['log']['request_id'] = "{}{}".format(time.mktime(datetime.timetuple(st)),randint(1, 1000000))
                sys_weblog['log']['st'] = time.mktime(datetime.timetuple(st))*1000 + st.microsecond/1000
                sys_weblog['log']['ip'] = request.remote_addr
                sys_weblog['log']['url'] = request.url
                g.request_id = sys_weblog['log']['request_id']
                if not sys_weblog['user'].is_anonymous:
                    sys_weblog['user']['user_id'] = g.user.id


            @app.teardown_request
            def teardown_request(exception):
                et = datetime.utcnow()
                try:
                    sys_weblog['log']['et'] = time.mktime(datetime.timetuple(et))*1000 + et.microsecond/1000
                    sys_weblog['log']['u_t_m'] = g.log['et'] - g.log['st']
                    logging.getLogger("r_log").info(g.log)
                    if exception:
                        logging.getLogger("err_log").exception("Exception")
                        logging.getLogger("err_log").error(g.log)
                except:
                    pass
