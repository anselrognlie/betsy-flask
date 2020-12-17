import pytest

from flask import url_for

import betsy.views.helper.order_helper as order_helper
from betsy.models.product import Product
from betsy.models.order import Order
from betsy.errors.model_error import ModelError

from ..test_lib.helpers.cart_test_mixin import CartTestMixin
from ..test_lib.helpers.flask_helper import assert_flashes, assert_no_flashes, perform_login
from ..test_lib.helpers.model_helpers import (
    add_order_product, make_merchant, make_order_with_status,
    make_product, make_order, make_order_hash
)
from ..test_lib.mocks.mock_attributes import MockAttributes
from ..test_lib.mocks.simple_mocker import SimpleMocker

def test_show_cart(app, client):
    with app.test_request_context():
        result = client.get(url_for('order.cart'))

        assert result.status_code == 200

def test_show_cart_after_loaded(app, client):
    with app.test_request_context():
        client.get(url_for('order.cart'))
        result = client.get(url_for('order.cart'))

        assert result.status_code == 200

def test_show_cart_failure(app, client):
    def no_cart():
        return None

    mock = MockAttributes()
    mock.register(order_helper, 'get_cart', no_cart)

    with app.test_request_context(), SimpleMocker([mock]):
        result = client.get(url_for('order.cart'))

        assert result.status_code == 302
        assert result.location.endswith(url_for('page.home'))
        assert_flashes(client, 'Unable to create cart', 'error')

class TestShopping(CartTestMixin):
    # pylint: disable=no-self-use
    @pytest.fixture(autouse=True)
    def before(self, app, session, client):
        with app.app_context():
            count = 5
            merchants = [make_merchant(session, i) for i in range(count)]
            products = [make_product(session, i, merchants[i]) for i in range(count)]

            # pylint: disable=attribute-defined-outside-init
            self.app = app
            self.session = session
            self.client = client
            self.merchant_ids = [merchant.id for merchant in merchants]
            self.product_ids = [product.id for product in products]

    def test_add_product_to_cart(self):
        with self.app.test_request_context():
            result = self.client.post(
                url_for('order.add_product', product_id=self.product_ids[0]),
                data=dict(quantity=1))

            items = self.get_cart_items()

            assert len(items) == 1
            assert items[0].quantity == 1
            assert items[0].product_id == self.product_ids[0]
            assert result.status_code == 302
            assert result.location.endswith(url_for('order.cart'))

    def test_add_invalid_product_to_cart(self):
        with self.app.test_request_context():
            result = self.client.post(
                url_for('order.add_product', product_id=-1),
                data=dict(quantity=1))

            items = self.get_cart_items()

            assert len(items) == 0
            assert result.status_code == 302
            assert result.location.endswith(url_for('product.index'))
            assert_flashes(self.client, 'Could not find product: -1', 'error')

    def test_add_invalid_quantity_to_cart(self):
        with self.app.test_request_context():
            result = self.client.post(
                url_for('order.add_product', product_id=self.product_ids[0]),
                data=dict(quantity=2))

            items = self.get_cart_items()

            assert len(items) == 0
            assert result.status_code == 302
            assert result.location.endswith(url_for('product.show', id=self.product_ids[0]))
            assert_flashes(self.client, 'Could not add requested product quantity', 'error')

    def test_update_product_in_cart(self):
        with self.app.test_request_context():
            self.client.post(
                url_for('order.add_product', product_id=self.product_ids[1]),
                data=dict(quantity=1))

            result = self.client.post(
                url_for('order.update_product', product_id=self.product_ids[1]),
                data=dict(quantity=2))

            items = self.get_cart_items()

            assert len(items) == 1
            assert items[0].quantity == 2
            assert items[0].product_id == self.product_ids[1]
            assert result.status_code == 302
            assert result.location.endswith(url_for('order.cart'))

    def test_update_invalid_product_in_cart(self):
        with self.app.test_request_context():
            result = self.client.post(
                url_for('order.update_product', product_id=-1),
                data=dict(quantity=1))

            items = self.get_cart_items()

            assert len(items) == 0
            assert result.status_code == 302
            assert result.location.endswith(url_for('product.index'))

    def test_update_product_not_in_cart(self):
        with self.app.test_request_context():
            self.client.post(
                url_for('order.add_product', product_id=self.product_ids[1]),
                data=dict(quantity=2))

            result = self.client.post(
                url_for('order.update_product', product_id=self.product_ids[0]),
                data=dict(quantity=1))

            items = self.get_cart_items()

            assert len(items) == 1
            assert items[0].quantity == 2
            assert items[0].product_id == self.product_ids[1]
            assert result.status_code == 302
            assert result.location.endswith(url_for('product.show', id=self.product_ids[0]))
            assert_flashes(self.client, 'Could not update requested product quantity', 'error')

    def test_get_checkout_cart(self):
        with self.app.test_request_context():
            self.client.post(
                url_for('order.add_product', product_id=self.product_ids[1]),
                data=dict(quantity=1))

            result = self.client.get(url_for('order.checkout'))

            assert result.status_code == 200

    def test_get_checkout_empty_cart(self):
        with self.app.test_request_context():

            result = self.client.get(url_for('order.checkout'))

            assert result.status_code == 302
            assert result.location.endswith(url_for('order.cart'))
            assert_flashes(self.client, 'Unable to process checkout', 'error')

    def test_post_failed_checkout(self):
        def checkout_raise(*args, **kwargs):
            raise ModelError()

        mock = MockAttributes()
        mock.register(Order, 'checkout', checkout_raise)

        with self.app.test_request_context(), SimpleMocker([mock]):
            self.client.post(
                url_for('order.add_product', product_id=self.product_ids[1]),
                data=dict(quantity=2))

            result = self.client.post(url_for('order.checkout'), data=dict(make_order_hash(0)))

            assert result.status_code == 200
            assert b'Unable to complete checkout' in result.data

    def test_post_checkout(self):
        with self.app.test_request_context():
            self.client.post(
                url_for('order.add_product', product_id=self.product_ids[1]),
                data=dict(quantity=2))
            cart = self.get_cart()

            result = self.client.post(url_for('order.checkout'), data=dict(make_order_hash(0)))

            new_cart = self.get_cart()

            assert result.status_code == 302
            assert result.location.endswith(url_for('order.show', id=cart.id))
            assert not new_cart

    def test_show_order(self):
        with self.app.test_request_context():
            order = make_order(self.session, 0)
            product = Product.find_by_id(self.product_ids[1])
            add_order_product(self.session, order, product, 3)

            result = self.client.get(url_for('order.show', id=order.id))

            assert result.status_code == 200

    def test_show_invalid_order(self):
        with self.app.test_request_context():
            result = self.client.get(url_for('order.show', id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(self.client, 'Invalid order', 'error')

    def test_cancel_order(self):
        with self.app.test_request_context():
            order = make_order_with_status(self.session, 1)
            product = Product.find_by_id(self.product_ids[1])
            add_order_product(self.session, order, product, 3)

            result = self.client.post(url_for('order.cancel', id=order.id))

            assert result.status_code == 302
            assert result.location.endswith(url_for('order.show', id=order.id))
            assert_no_flashes(self.client)

    def test_cancel_invalid_order(self):
        with self.app.test_request_context():
            result = self.client.post(url_for('order.cancel', id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(self.client, 'Invalid order', 'error')

    def test_cancel_not_cancellable_order(self):
        with self.app.test_request_context():
            order = make_order_with_status(self.session, 0)
            product = Product.find_by_id(self.product_ids[1])
            add_order_product(self.session, order, product, 1)

            result = self.client.post(url_for('order.cancel', id=order.id))

            assert result.status_code == 302
            assert result.location.endswith(url_for('order.show', id=order.id))
            assert_flashes(self.client, 'Unable to cancel order', 'error')

    def test_order_details(self):
        with self.app.test_request_context():
            perform_login(self.client, make_merchant(self.session,0))

            order = make_order_with_status(self.session, 1)
            product = Product.find_by_id(self.product_ids[1])
            add_order_product(self.session, order, product, 3)

            result = self.client.get(url_for('order.details', id=order.id))

            assert result.status_code == 200

    def test_invalid_order_details(self):
        with self.app.test_request_context():
            perform_login(self.client, make_merchant(self.session, 0))

            result = self.client.get(url_for('order.details', id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(self.client, 'Invalid order', 'error')
