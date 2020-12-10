https://flask.palletsprojects.com/en/1.1.x/quickstart/

https://jinja.palletsprojects.com/en/2.11.x/templates/

https://realpython.com/flask-by-example-part-1-project-setup/

$ mkdir myproject
$ cd myproject
$ python3 -m venv venv

$ . venv/bin/activate

$ pip install flask
$ pip install pylint-flask

$ pip install -e .

createdb db_root_dev
dropdb db_root_dev

createdb db_root_test
dropdb db_root_test


# configuration file

$ touch config.py
```python
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# secret key
$ python -c 'import os; print(os.urandom(16))'

# make sure the vscode python is the venv version

```python
# pylint: disable=missing-module-docstring

from flask import Flask
app = Flask(__name__)
settings_obj = os.environ.get('APP_SETTINGS', default='config.DevelopmentConfig')
app.config.from_object(settings_obj)

@app.route('/')
def hello_world():
    # pylint: disable=missing-function-docstring
    return 'Hello, World!'
```

$ export FLASK_APP=hello.py
$ export FLASK_ENV=development
or
$ export FLASK_DEBUG=1
$ flask run

# add --host=0.0.0.0 to be externally visible

or

$ FLASK_APP=hello.py flask run

or

$ FLASK_APP=hello.py python -m flask run

# configuration stuff

APP_SETTINGS=config.DevelopmentConfig FLASK_APP=hello.py python -m flask run

# database stuff

$ python -m pip install psycopg2==2.8.4 Flask-SQLAlchemy===2.4.1 Flask-Migrate==2.5.2
$ python -m pip freeze > requirements.txt
$ pip install -r requirements.txt


$ LDFLAGS='-L/usr/local/lib -L/usr/local/opt/openssl/lib
-L/usr/local/opt/readline/lib' python -m pip install psycopg2

or

$ python -m pip install psycopg2-binary

$ python -m pip install flask-sqlalchemy
$ python -m pip install flask-migrate
$ python -m pip install pylint-flask-sqlalchemy

$ export DATABASE_URL="postgresql:///wordcount_dev"

```python
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
```

% FLASK_APP=task_list python -m flask db init
% FLASK_APP=task_list python -m flask db migrate -m "Initial migration."
% FLASK_APP=task_list python -m flask db upgrade

% FLASK_APP=task_list FLASK_ENV=development FLASK_DEBUG=1 python -m flask run

pylint --generate-rcfile > .pylintrc

[MASTER]
init-hook='import sys; sys.path.append(".")'

heroku
======
heroku git:remote -a <site-name>
heroku addons:create heroku-postgresql:hobby-dev

Database has been created and is available
 ! This database is empty. If upgrading, you can transfer
 ! data from another database with pg:copy
Created postgresql-curly-84169 as DATABASE_URL
Use heroku addons:docs heroku-postgresql to view documentation

Procfile
==========
web: FLASK_APP=betsy FLASK_ENV=production python -m flask run

Test
----

    $ python -m pytest

Run with coverage report::

    $ python -m coverage run -m pytest
    $ python -m coverage report
    $ python -m coverage html  # open htmlcov/index.html in a browser

Configuration
===============
instance/
 +-config.py
 +-development.py
 +-production.py
 +-staging.py
 +-testing.py

config.py:
============
import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TESTING = False
CSRF_ENABLED = True
SECRET_KEY = b'some key'
SQLALCHEMY_TRACK_MODIFICATIONS = False
ALLOW_IMPERSONATION = False

development.py:
==================
DEVELOPMENT = True
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'postgresql:///betsy_dev'
ALLOW_IMPERSONATION = True

production.py:
==================
DEBUG = False
SQLALCHEMY_DATABASE_URI = 'postgresql:///betsy_prod'

staging.py:
==================
DEVELOPMENT = True
DEBUG = True

testing.py:
==================
TESTING = True
SQLALCHEMY_DATABASE_URI = 'postgresql:///betsy_tst'
ALLOW_IMPERSONATION = True
WTF_CSRF_ENABLED = False


.env
=============
export GITHUB_CLIENT_ID=some_client_id
export GITHUB_CLIENT_SECRET=some_client_secret


Packages
=============

https://github-flask.readthedocs.io/en/latest/
https://pythonhosted.org/Flask-OAuth/  # not currently used, but may replace github
https://flask-login.readthedocs.io/en/latest/  # not used, more research needed
https://wtforms.readthedocs.io/en/2.3.x/
https://flask-wtf.readthedocs.io/en/stable/

References
=============
https://pytest.org/en/latest/reference.html#hook-reference
https://flask.palletsprojects.com/en/1.1.x/testing/
