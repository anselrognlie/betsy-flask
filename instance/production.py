import os
from distutils.util import strtobool

def simple_bool(value):
    if hasattr(value, 'lower'):
        return strtobool(value)
    return value

def utf8_string(value):
    return bytes(value, "utf-8").decode("unicode_escape")

# pylint: disable=line-too-long
SECRET_KEY = utf8_string(os.environ['SECRET_KEY'])
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
TESTING = simple_bool(os.environ.get('TESTING', False))
DEBUG = simple_bool(os.environ.get('DEBUG', False))
CSRF_ENABLED = simple_bool(os.environ.get('CSRF_ENABLED', True))
SQLALCHEMY_TRACK_MODIFICATIONS = simple_bool(os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', False))
ALLOW_IMPERSONATION = simple_bool(os.environ.get('ALLOW_IMPERSONATION', False))
