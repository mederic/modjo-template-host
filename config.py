import os

_basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfiguration(object):
    DEBUG = True
    TESTING = False

    ADMIN_SECRET = 'SecretKey'

    ANYONE_CAN_UPLOAD = True

    TEMPLATE_FOLDER = os.path.join(_basedir, "templates")

    DATABASE_URI = 'sqlite:///app.db'
