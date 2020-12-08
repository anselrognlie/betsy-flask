from flask import url_for

from betsy.models.merchant import Merchant

from ..test_lib.helpers.flask_helper import assert_flashes
from ..test_lib.mocks.simple_mocker import SimpleMocker
from ..test_lib.mocks.mock_auth import MockAuth

def make_auth_hash():
    return dict(
        uid='uid',
        email='uid@email.com',
        name='UID',
        provider='github'
    )

def test_auth_flow_for_new_user(app, client):
    with app.test_request_context(), SimpleMocker([MockAuth(make_auth_hash())]):

        client.get(url_for('auth.authorized'))

        merchant = Merchant.query.first()
        assert merchant.uid == 'uid'
        assert merchant.email == 'uid@email.com'
        assert merchant.name == 'UID'
        assert merchant.provider == 'github'

def test_auth_flow_for_existing_user(app, session, client):
    with app.test_request_context(), SimpleMocker([MockAuth(make_auth_hash())]):
        session.add(Merchant(**make_auth_hash()))
        session.commit()

        client.get(url_for('auth.authorized'))

        merchant = Merchant.query.first()
        assert merchant.uid == 'uid'
        assert merchant.email == 'uid@email.com'
        assert merchant.name == 'UID'
        assert merchant.provider == 'github'

def test_auth_flow_for_unauthorized_user(app, client):
    with app.test_request_context(), SimpleMocker([MockAuth(make_auth_hash(), authorized=False)]):

        result = client.get(url_for('auth.authorized'))

        merchant = Merchant.query.first()
        assert merchant is None
        assert result.status_code == 302
        assert result.location.endswith(url_for('page.home'))
        assert_flashes(client, 'Authorization failed.')

def test_login(app, client):
    with app.test_request_context(), SimpleMocker([MockAuth(make_auth_hash())]):

        result = client.post(url_for('auth.login'))

        assert result.status_code == 302
        assert result.location.endswith(url_for('auth.authorized'))
