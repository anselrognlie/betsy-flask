import pytest

from flask import url_for

from betsy import create_app
from betsy.keys import LOGGED_IN_USER_ID
from betsy.models.merchant import Merchant
from betsy.storage.db import db
from betsy.logging.logger import logger

from ..test_lib.mocks.simple_mocker import SimpleMocker
from ..test_lib.helpers.flask_helper import assert_flashes, perform_login
from ..test_lib.helpers.model_helpers import (
    make_merchant
)
from ..test_lib.mocks.mock_attributes import MockAttributes

def test_impersonate_merchant_when_not_allowed():
    app = create_app(dict(TESTING=True, ALLOW_IMPERSONATION=False))

    with app.test_request_context():
        merchants = [make_merchant(db.session, i) for i in range(5)]
        merchant = merchants[0]
        client = app.test_client()

        result = client.post(url_for('merchant.impersonate', id=merchant.id))

        assert result.status_code == 302
        assert result.location.endswith(url_for('page.home'))

        with client.session_transaction() as session:
            assert not session.get(LOGGED_IN_USER_ID)

class TestWithMerchants:
    # pylint: disable=no-self-use
    @pytest.fixture(autouse=True)
    def before(self, app, client, session):
        with app.app_context():
            merchants = [make_merchant(session, i) for i in range(5)]

            # pylint: disable=attribute-defined-outside-init
            self.app = app
            self.client = client
            self.session = session
            self.merchant_ids = [merchant.id for merchant in merchants]

    def perform_login(self):
        # with self.app.test_request_context():
        merchant = Merchant.find_by_id(self.merchant_ids[0])
        perform_login(self.client, merchant)
        return merchant

    def test_index(self):
        with self.app.test_request_context():
            assert self.client.get(url_for('merchant.index')).status_code == 200

    def test_show(self):
        with self.app.test_request_context():
            assert self.client.get(
                url_for('merchant.show', id=self.merchant_ids[0])
            ).status_code == 200

    def test_show_invalid_merchant(self):
        with self.app.test_request_context():
            result = self.client.get(url_for('merchant.show', id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('merchant.index'))

    def test_impersonate_merchant(self):
        with self.app.test_request_context():
            merchant = Merchant.find_by_id(self.merchant_ids[0])
            result = self.client.post(url_for('merchant.impersonate', id=merchant.id))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(self.client, f'Impersonating user: {merchant.name}', 'success')

            with self.client.session_transaction() as session:
                assert int(session[LOGGED_IN_USER_ID]) == merchant.id

    def test_impersonate_invalid_merchant(self):
        with self.app.test_request_context():
            result = self.client.post(url_for('merchant.impersonate', id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(self.client, 'Could not find user: -1', 'error')

            with self.client.session_transaction() as session:
                assert not session.get(LOGGED_IN_USER_ID)

    def test_logout_merchant(self):
        with self.app.test_request_context():
            merchant = self.perform_login()

            result = self.client.post(url_for('merchant.logout'))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(self.client, f'Logged out user: {merchant.name}', 'success')

            with self.client.session_transaction() as session:
                assert not session.get(LOGGED_IN_USER_ID)

    def test_merchant_dashboard(self):
        with self.app.test_request_context():
            self.perform_login()

            result = self.client.get(url_for('merchant.dashboard'))

            assert result.status_code == 200

    def test_merchant_required_login(self):
        with self.app.test_request_context():
            result = self.client.get(url_for('merchant.dashboard'))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(self.client, 'This feature requires being logged in', 'error')

            with self.client.session_transaction() as session:
                assert not session.get(LOGGED_IN_USER_ID)

    def test_merchant_products(self):
        with self.app.test_request_context():
            self.perform_login()

            result = self.client.get(url_for('merchant.products'))

            assert result.status_code == 200

    def test_merchant_orders(self):
        with self.app.test_request_context():
            self.perform_login()

            result = self.client.get(url_for('merchant.orders'))

            assert result.status_code == 200

    def test_merchant_get_update_form(self):
        with self.app.test_request_context():
            self.perform_login()

            result = self.client.get(url_for('merchant.update'))

            assert result.status_code == 200

    def test_merchant_post_update_form(self):
        with self.app.test_request_context():
            merchant = self.perform_login()

            result = self.client.post(url_for('merchant.update'), data=dict(
                name='new name'
            ))

            self.session.refresh(merchant)

            assert result.status_code == 302
            assert result.location.endswith(url_for('merchant.show', id=merchant.id))
            assert merchant.name == 'new name'

    def test_post_merchant_update_fails(self):
        mock = MockAttributes()

        def save_error():
            raise RuntimeError()
        mock.register(Merchant, 'save', save_error)

        errors = []
        def my_log(ex):
            errors.append(ex)
        mock.register(logger, 'exception', my_log)

        with self.app.test_request_context(), SimpleMocker([mock]):
            self.perform_login()

            result = self.client.post(url_for('merchant.update'), data=dict(
                name='new name'
            ))

            assert result.status_code == 200
            assert str(errors[0]) == 'failed to save merchant'
