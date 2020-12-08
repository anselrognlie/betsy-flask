# import datetime

import os
import pytest

from betsy import create_app
from betsy.storage.db import db

from betsy.models import *  # pylint: disable=wildcard-import

def make_test_data(db):  # pylint: disable=redefined-outer-name, invalid-name
    # pylint: disable=line-too-long
    pass
    # db.session.add(User(username='test', password=generate_password_hash('test')))
    # db.session.add(User(username='other', password=generate_password_hash('other')))
    # db.session.add(Post(title='test title', body='test\nbody', author_id=1, created=datetime.datetime(2018, 1, 1)))
    # db.session.commit()


def init_db():
    """Clear existing data and create new tables."""
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    # import yourapplication.models
    db.drop_all()
    db.create_all()

@pytest.fixture
def session():
    return db.session

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    os.environ['FLASK_ENV'] = 'TESTING'
    app = create_app({ 'TESTING': True })  # pylint: disable=redefined-outer-name

    # create the database and load test data
    with app.app_context():
        init_db()
        make_test_data(db)

    return app


@pytest.fixture
def client(app):  # pylint: disable=redefined-outer-name
    """A test client for the app."""
    return app.test_client()


# @pytest.fixture
# def runner(app):  # pylint: disable=redefined-outer-name
#     """A test runner for the app's Click commands."""
#     return app.test_cli_runner()


# class AuthActions:
#     def __init__(self, client):  # pylint: disable=redefined-outer-name
#         self._client = client

#     def login(self, username="test", password="test"):
#         return self._client.post(
#             "/auth/login", data={"username": username, "password": password}
#         )

#     def logout(self):
#         return self._client.get("/auth/logout")


# @pytest.fixture
# def auth(client):  # pylint: disable=redefined-outer-name
#     return AuthActions(client)
