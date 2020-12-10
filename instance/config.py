import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TESTING = False
CSRF_ENABLED = True
SECRET_KEY = b'\xecx\xfagV;\xda\xe6y\xd2tM\xfay\xb7\xe3'
SQLALCHEMY_TRACK_MODIFICATIONS = False
ALLOW_IMPERSONATION = False
