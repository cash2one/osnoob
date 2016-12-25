from pymongo import MongoClient

__author__ = 'woo'
class PyMongo():

    def __init__(self, app=None, config_prefix='MONGO', db_config= None):
        if app or db_config:
            self.init_app(app, config_prefix, db_config)
        pass

    def init_app(self, app=None, config_prefix='MONGO', db_config= None):

        if app and db_config:
            raise Exception("parameter: app or db_config must be None")
        if app:
            def key(suffix):
                return '%s_%s' % (config_prefix, suffix)
            if key('URI') in app.config:

                # connection
                config = app.config[key('URI')]

                if config['replica_set']:
                    connection = MongoClient(
                        config['mongodb'],
                        fsync=config['fsync'],
                        read_preference = config['read_preference'],
                        replicaSet = config['replica_set']
                        )

                else:
                    connection = MongoClient(
                        config['mongodb'],
                        fsync=config['fsync'],
                        read_preference = config['read_preference'],
                        )
                self.name = config['db']
                self.dbs = connection[config['db']]
                self.db = Conlections(self.dbs)

        elif db_config:

            # connection
            config = app

            if config['replica_set']:
                connection = MongoClient(
                    config['mongodb'],
                    fsync=config['fsync'],
                    read_preference = config['read_preference'],
                    replica_set = config['replica_set']
                    )

            else:
                connection = MongoClient(
                    config['mongodb'],
                    fsync=config['fsync'],
                    read_preference = config['read_preference'],
                    )
            self.name = config['db']
            self.dbs = connection[config['db']]
            self.db = Conlections(self.dbs)

class Conlections():

    def __init__(self, conn_db = None):
        if conn_db:
            self.conlection_object(conn_db)

    def conlection_object(self, conn_db):

        for conlection in conn_db.collection_names():
            conn_db[conlection].__dict__["paging"] = self.paging()
            #print conlection
            self.__dict__[conlection] = conn_db[conlection]

    def paging(self):
        print self