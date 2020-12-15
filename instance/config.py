import os
basedir = os.path.abspath(os.path.dirname(__file__))

def utf8_string(value):
    return bytes(value, "utf-8").decode("unicode_escape")

DEBUG = False
TESTING = False
CSRF_ENABLED = True
SECRET_KEY = utf8_string(os.environ['SECRET_KEY'])
SQLALCHEMY_TRACK_MODIFICATIONS = False
ALLOW_IMPERSONATION = False
