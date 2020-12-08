from flask import url_for

from betsy.keys import CART_ID

# from http://blog.paulopoiati.com/2013/02/22/testing-flash-messages-in-flask/
def assert_flashes(client, expected_message, expected_category='message'):
    with client.session_transaction() as session:
        try:
            category, message = session['_flashes'][0]
        except KeyError as key_error:
            raise AssertionError('nothing flashed') from key_error
        assert expected_message in message
        assert expected_category == category

def assert_no_flashes(client):
    with client.session_transaction() as session:
        assert not session.get('_flashes')

def clear_flash(client):
    with client.session_transaction() as session:
        session.pop('_flashes', None)

def get_cart_id(client):
    with client.session_transaction() as session:
        return session.get(CART_ID, None)

def perform_login(client, merchant):
    # with self.app.test_request_context():
    client.post(url_for('merchant.impersonate', id=merchant.id))
    clear_flash(client)
