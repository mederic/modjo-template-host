import os

_basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfiguration(object):
    DEBUG = False
    TESTING = False

    ADMIN_SECRET = 'SecretKey'

    ANYONE_CAN_UPLOAD = True

    TEMPLATE_FOLDER = os.path.join(_basedir, "modjoTemplates")

    DATABASE_URI = 'sqlite:///app.db'
