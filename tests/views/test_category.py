import pytest

import flask
from flask import url_for

from betsy.models.category import Category
from betsy.models.merchant import Merchant
from betsy.logging.logger import logger

from ..test_lib.helpers.flask_helper import assert_flashes, perform_login
from ..test_lib.helpers.model_helpers import (
    make_category, make_merchant
)
from ..test_lib.mocks.simple_mocker import SimpleMocker
from ..test_lib.mocks.mock_attributes import MockAttributes
from ..test_lib.mocks.mock_flash import MockFlash

class TestWithSetup:
    # pylint: disable=no-self-use
    @pytest.fixture(autouse=True)
    def before(self, app, client, session):
        with app.app_context():
            merchants = [make_merchant(session, i) for i in range(5)]
            categories = [make_category(session, i) for i in range(5)]

            # pylint: disable=attribute-defined-outside-init
            self.app = app
            self.client = client
            self.session = session
            self.category_ids = [category.id for category in categories]
            self.merchant_ids = [merchant.id for merchant in merchants]

    def perform_login(self):
        # with self.app.test_request_context():
        merchant = Merchant.find_by_id(self.merchant_ids[0])
        perform_login(self.client, merchant)
        return merchant

    def test_index(self):
        with self.app.test_request_context():
            assert self.client.get(url_for('category.index')).status_code == 200

    def test_show_category(self):
        with self.app.test_request_context():
            result = self.client.get(url_for('category.show', id=self.category_ids[0]))

            assert result.status_code == 200

    def test_show_invalid_category(self):
        with self.app.test_request_context():
            result = self.client.get(url_for('category.show', id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('category.index'))
            assert_flashes(self.client, 'Could not find category: -1', 'error')

    def test_get_create_category(self):
        with self.app.test_request_context():
            self.perform_login()

            result = self.client.get(url_for('category.create'))

            assert result.status_code == 200

    def test_get_update_category(self):
        with self.app.test_request_context():
            self.perform_login()

            result = self.client.get(url_for('category.update', id=self.category_ids[0]))

            assert result.status_code == 200

    def test_post_create_category(self):
        with self.app.test_request_context():
            self.perform_login()

            result = self.client.post(url_for('category.create'), data=dict(
                name='new category'
            ))

            category = Category.query.order_by(Category.id.desc()).first()

            assert result.status_code == 302
            assert result.location.endswith(url_for('category.show', id=category.id))
            assert category.name == 'new category'

    def test_post_update_category(self):
        with self.app.test_request_context():
            self.perform_login()

            category_id = self.category_ids[0]
            result = self.client.post(url_for('category.update', id=category_id), data=dict(
                name='new category'
            ))

            category = Category.find_by_id(category_id)

            assert result.status_code == 302
            assert result.location.endswith(url_for('category.show', id=category.id))
            assert category.name == 'new category'

    def test_post_create_category_fails(self):
        mock = MockAttributes()

        def save_error():
            raise RuntimeError()
        mock.register(Category, 'save', save_error)

        errors = []
        def my_log(ex):
            errors.append(ex)
        mock.register(logger, 'exception', my_log)

        with self.app.test_request_context(), SimpleMocker([mock]):
            self.perform_login()

            result = self.client.post(url_for('category.create'), data=dict(
                name='new category'
            ))

            assert result.status_code == 200
            assert str(errors[0]) == 'failed to save category'

    def test_post_create_invalid_category(self):
        mock = MockAttributes()

        errors = []
        def my_log(ex):
            errors.append(ex)
        mock.register(logger, 'exception', my_log)

        mock_flash = MockFlash()
        mock.register(flask, 'flash', mock_flash.flash)

        with self.app.test_request_context(), SimpleMocker([mock]):
            category = Category.find_by_id(self.category_ids[0])

            self.perform_login()

            result = self.client.post(url_for('category.create'), data=dict(
                name=category.name
            ))

            assert result.status_code == 200
            assert len(errors) == 1
            assert str(errors[0]) == 'failed to save category'
            assert len(mock_flash.flashes) == 2
