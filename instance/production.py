import os

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SECRET_KEY = os.environ['SECRET_KEY']
TESTING = os.environ.get('TESTING', False)
DEBUG = os.environ.get('DEBUG', False)
CSRF_ENABLED = os.environ.get('CSRF_ENABLED', True)
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
ALLOW_IMPERSONATION = os.environ.get('ALLOW_IMPERSONATION', False)
