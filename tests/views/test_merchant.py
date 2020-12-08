import pytest

from flask import url_for

from betsy import create_app
from betsy.keys import LOGGED_IN_USER_ID
from betsy.models.merchant import Merchant
from betsy.storage.db import db

from ..test_lib.helpers.flask_helper import assert_flashes, perform_login
from ..test_lib.helpers.model_helpers import (
    make_merchant
)

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
    def before(self, app, session):
        with app.app_context():
            merchants = [make_merchant(session, i) for i in range(5)]

            # pylint: disable=attribute-defined-outside-init
            self.app = app
            self.merchant_ids = [merchant.id for merchant in merchants]

    def perform_login(self, client):
        # with self.app.test_request_context():
        merchant = Merchant.find_by_id(self.merchant_ids[0])
        perform_login(client, merchant)
        return merchant

    def test_index(self, app, client):
        with app.test_request_context():
            assert client.get(url_for('merchant.index')).status_code == 200

    def test_show(self, app, client):
        with app.test_request_context():
            assert client.get(url_for('merchant.show', id=self.merchant_ids[0])).status_code == 200

    def test_show_invalid_merchant(self, app, client):
        with app.test_request_context():
            result = client.get(url_for('merchant.show', id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('merchant.index'))

    def test_impersonate_merchant(self, app, client):
        with app.test_request_context():
            merchant = Merchant.find_by_id(self.merchant_ids[0])
            result = client.post(url_for('merchant.impersonate', id=merchant.id))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(client, f'Impersonating user: {merchant.name}', 'success')

            with client.session_transaction() as session:
                assert int(session[LOGGED_IN_USER_ID]) == merchant.id

    def test_impersonate_invalid_merchant(self, app, client):
        with app.test_request_context():
            result = client.post(url_for('merchant.impersonate', id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(client, 'Could not find user: -1', 'error')

            with client.session_transaction() as session:
                assert not session.get(LOGGED_IN_USER_ID)

    def test_logout_merchant(self, app, client):
        with app.test_request_context():
            merchant = self.perform_login(client)

            result = client.post(url_for('merchant.logout'))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(client, f'Logged out user: {merchant.name}', 'success')

            with client.session_transaction() as session:
                assert not session.get(LOGGED_IN_USER_ID)

    def test_merchant_dashboard(self, app, client):
        with app.test_request_context():
            self.perform_login(client)

            result = client.get(url_for('merchant.dashboard'))

            assert result.status_code == 200

    def test_merchant_required_login(self, app, client):
        with app.test_request_context():
            result = client.get(url_for('merchant.dashboard'))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(client, 'This feature requires being logged in', 'error')

            with client.session_transaction() as session:
                assert not session.get(LOGGED_IN_USER_ID)

    def test_merchant_products(self, app, client):
        with app.test_request_context():
            self.perform_login(client)

            result = client.get(url_for('merchant.products'))

            assert result.status_code == 200

    def test_merchant_orders(self, app, client):
        with app.test_request_context():
            self.perform_login(client)

            result = client.get(url_for('merchant.orders'))

            assert result.status_code == 200

    def test_merchant_get_update_form(self, app, client):
        with app.test_request_context():
            self.perform_login(client)

            result = client.get(url_for('merchant.update'))

            assert result.status_code == 200

    def test_merchant_post_update_form(self, app, client, session):
        with app.test_request_context():
            merchant = self.perform_login(client)

            result = client.post(url_for('merchant.update'), data=dict(
                name='new name'
            ))

            session.refresh(merchant)

            assert result.status_code == 302
            assert result.location.endswith(url_for('merchant.show', id=merchant.id))
            assert merchant.name == 'new name'
