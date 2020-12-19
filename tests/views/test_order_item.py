import pytest
from datetime import datetime

from flask import url_for

from betsy.models.merchant import Merchant
from betsy.models.product import Product

from ..test_lib.mocks.mock_now import MockNow
from ..test_lib.mocks.simple_mocker import SimpleMocker
from ..test_lib.helpers.cart_test_mixin import CartTestMixin
from ..test_lib.helpers.flask_helper import (
    assert_flashes, assert_no_flashes, clear_flash, perform_login
)
from ..test_lib.helpers.model_helpers import (
    add_order_product, make_order_with_status, make_product
)

class TestWithSetup(CartTestMixin):
    # pylint: disable=no-self-use
    @pytest.fixture(autouse=True)
    def before(self, app, client, session):
        with app.app_context():
            products = [make_product(session, i) for i in range(5)]

            # pylint: disable=attribute-defined-outside-init
            self.app = app
            self.client = client
            self.session = session
            self.product_ids = [product.id for product in products]
            self.merchant_ids = [product.merchant.id for product in products]

    def perform_login(self):
        # with self.app.test_request_context():
        merchant = Merchant.find_by_id(self.merchant_ids[0])
        self.client.post(url_for('merchant.impersonate', id=merchant.id))
        clear_flash(self.client)
        return merchant

    def test_delete_from_cart(self):
        with self.app.test_request_context():
            self.client.post(
                url_for('order.add_product', product_id=self.product_ids[1]),
                data=dict(quantity=1))

            items = self.get_cart_items()
            result = self.client.post(url_for('order_item.delete', id=items[0].id))

            items = self.get_cart_items()
            assert len(items) == 0
            assert result.status_code == 302
            assert result.location.endswith(url_for('order.cart'))
            assert_no_flashes(self.client)

    def test_delete_invalid_item_from_cart(self):
        with self.app.test_request_context():
            self.client.post(
                url_for('order.add_product', product_id=self.product_ids[1]),
                data=dict(quantity=1))

            result = self.client.post(url_for('order_item.delete', id=-1))

            items = self.get_cart_items()
            assert len(items) == 1
            assert result.status_code == 302
            assert result.location.endswith(url_for('order.cart'))
            assert_flashes(self.client, 'Could not update order', 'error')

    def test_delete_item_from_invalid_cart(self):
        with self.app.test_request_context():
            order = make_order_with_status(self.session, 1)
            product = Product.find_by_id(self.product_ids[1])
            item = add_order_product(self.session, order, product, 5)

            result = self.client.post(url_for('order_item.delete', id=item.id))

            items = order.order_items.all()
            assert len(items) == 1
            assert result.status_code == 302
            assert result.location.endswith(url_for('order.cart'))
            assert_flashes(self.client, 'Failed to delete order item', 'error')

    def test_ship_item(self):
        with self.app.test_request_context(), SimpleMocker([MockNow(datetime(2020, 9, 1))]):
            order = make_order_with_status(self.session, 1)
            product = Product.find_by_id(self.product_ids[1])
            item = add_order_product(self.session, order, product, 5)

            merchant = product.merchant
            perform_login(self.client, merchant)

            result = self.client.post(url_for('order_item.ship', id=item.id))

            item.reload()
            assert item.shipped_date == datetime(2020, 9, 1)
            assert result.status_code == 302
            assert result.location.endswith(url_for('merchant.orders'))
            assert_no_flashes(self.client)

    def test_ship_invalid_item(self):
        with self.app.test_request_context(), SimpleMocker([MockNow(datetime(2020, 9, 1))]):
            merchant = Merchant.find_by_id(self.merchant_ids[0])
            perform_login(self.client, merchant)

            result = self.client.post(url_for('order_item.ship', id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('merchant.orders'))
            assert_flashes(self.client, 'Could not ship order', 'error')

    def test_ship_item_for_invalid_order(self):
        with self.app.test_request_context(), SimpleMocker([MockNow(datetime(2020, 9, 1))]):
            order = make_order_with_status(self.session, 0)
            product = Product.find_by_id(self.product_ids[1])
            item = add_order_product(self.session, order, product, 5)

            merchant = product.merchant
            perform_login(self.client, merchant)

            result = self.client.post(url_for('order_item.ship', id=item.id))

            assert result.status_code == 302
            assert result.location.endswith(url_for('merchant.orders'))
            assert_flashes(self.client, 'Failed to ship order item', 'error')
