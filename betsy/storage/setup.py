# pylint: disable=missing-module-docstring
from .db import migrate
from ..models import * # pylint: disable=unused-import, wildcard-import

def register_db(app, db):
    '''
    Setup the db config
    '''
    # pylint: disable=invalid-name
    db.init_app(app)
    migrate.init_app(app, db)

def init_app(app, db):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    # pylint: disable=invalid-name
    register_db(app, db)
