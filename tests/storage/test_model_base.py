from tests.test_lib.mocks.mock_session import MockSession
from betsy.models.category import Category
from betsy.storage.model_base import ModelBase

from ..test_lib.helpers.model_helpers import (
    make_category
)
from ..test_lib.mocks.mock_attributes import MockAttributes
from ..test_lib.mocks.simple_mocker import SimpleMocker

def test_update_ignores_invalid_fields(app, session):
    with app.app_context():
        category = make_category(session, 0)

        category.update(name='new name', invalid_field=True)

        assert category.name == 'new name'
        assert not hasattr(category, 'invalid_field')

def test_update_in_transaction(app, session):
    with app.app_context():
        category = make_category(session, 0)

        with Category.transaction():
            category.update(name='new name')

        assert category.name == 'new name'

def test_transaction(app):
    class SessionHost:
        def __init__(self, session):
            self.session = session

    mock_session = MockSession()
    session_host = SessionHost(mock_session)
    def mock_db():
        return session_host

    mock = MockAttributes()
    mock.register(ModelBase, 'db', mock_db)

    with app.app_context(), SimpleMocker([mock]):
        with Category.transaction():
            pass

    assert mock_session.commit_called
    assert not mock_session.rollback_called

def test_destroy(app, session):
    with app.app_context():
        category = make_category(session, 0)
        category_id = category.id

        category.destroy()

        category = Category.find_by_id(category_id)
        assert not category

def test_destroy_in_transaction(app, session):
    with app.app_context():
        category = make_category(session, 0)
        category_id = category.id

        with Category.transaction():
            category.destroy()

        category = Category.find_by_id(category_id)
        assert not category
