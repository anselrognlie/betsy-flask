import os
basedir = os.path.abspath(os.path.dirname(__file__))


DEBUG = False
TESTING = False
CSRF_ENABLED = True
SECRET_KEY = 'set secret key'
SQLALCHEMY_TRACK_MODIFICATIONS = False
ALLOW_IMPERSONATION = False
