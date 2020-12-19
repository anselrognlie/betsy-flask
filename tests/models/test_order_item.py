import datetime
import pytest
from datetime import date

from betsy.models.merchant import Merchant
from betsy.models.product import Product
from betsy.models.order_item import OrderItem
from betsy.models.order import Order
from betsy.errors.model_error import ModelError

from ..test_lib.helpers.model_helpers import (
    add_order_product, make_product, make_order_with_status
)

class TestWithSimpleItemSetup:
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        with app.app_context():
            order = Order.make_cart()
            product = make_product(session, 0)
            item = add_order_product(session, order, product, 1)

            # pylint: disable=attribute-defined-outside-init
            self.order_id = order.id
            self.product_id = product.id
            self.item_id = item.id

    def test_order_item_repr(self, app):
        with app.app_context():
            # test that repr gives a nice string
            item = OrderItem.find_by_id(self.item_id)

            debug_str = repr(item)

            assert debug_str == f"<OrderItem product_id='{self.product_id}' order_id='{self.order_id}'>"  # pylint: disable=line-too-long

    def test_order_item_product_name(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)

            name = item.product_name()

            assert name == 'product-0'

    def test_order_item_product_price(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)

            price = item.product_price()

            assert price == 1000

    def test_order_item_subtotal(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)

            result = item.subtotal()

            assert result == 1000

    def test_order_item_product_availability(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)

            available = item.is_product_available()

            assert available

    def test_order_item_is_valid(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)

            result = item.is_valid()

            assert result

    def test_order_item_is_not_valid(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)
            item.quantity = 10

            result = item.is_valid()

            assert not result

    def test_order_item_prepare_checkout(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)

            item.prepare_checkout()

            assert item.purchase_price == item.product.price
            assert item.product.stock == 0

    def test_order_item_remove_from_cart(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)

            item.delete()
            item = OrderItem.find_by_id(self.item_id)

            assert item is None

    def test_order_item_cannot_remove_from_noncart(self, app, session):
        with app.app_context():
            orders = [make_order_with_status(session, i) for i in range(1, 3 + 1)]
            product = Product.find_by_id(self.product_id)
            items = [add_order_product(session, order, product, 1) for order in orders]

            for item in items:
                with pytest.raises(ModelError):
                    item.delete()

    def test_order_item_quantity_required(self, app, session):
        with app.app_context():
            order = make_order_with_status(session, 0)
            product = Product.find_by_id(self.product_id)

            with pytest.raises(ModelError):
                OrderItem(order=order, product=product, quantity=0).save()

    def test_order_item_must_be_valid_for_paid_order(self, app, session):
        with app.app_context():
            paid_order = make_order_with_status(session, 1)
            product = Product.find_by_id(self.product_id)

            with pytest.raises(ModelError):
                OrderItem(order=paid_order, product=product, quantity=1).save()

    def test_order_item_must_be_valid_when_shipped(self, app, session):
        with app.app_context():
            order = make_order_with_status(session, 1)
            product = Product.find_by_id(self.product_id)
            item = add_order_product(session, order, product, 1)

            with pytest.raises(ModelError):
                item.shipped_date = datetime.datetime(2020, 9, 1)
                item.purchase_price = None
                item.save()

class TestWithNonCartSetup:
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        with app.app_context():
            order = make_order_with_status(session, 1)
            product = make_product(session, 0)
            item = add_order_product(session, order, product, 1)
            other_product = make_product(session, 1)

            # pylint: disable=attribute-defined-outside-init
            self.order_id = order.id
            self.product_id = product.id
            self.item_id = item.id
            self.other_merchant_id = other_product.merchant.id

    def test_order_item_cannot_ship_twice(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)
            item.shipped_date = date(2020, 9, 1)

            result = item.can_ship()

            assert not result

    def test_order_item_can_ship_from_paid_order(self, app, session):
        with app.app_context():
            order = make_order_with_status(session, 1)
            product = Product.find_by_id(self.product_id)
            item = add_order_product(session, order, product, 1)

            result = item.can_ship()

            assert result

    def test_order_item_cannot_ship_from_not_paid(self, app, session):
        with app.app_context():
            orders = [make_order_with_status(session, i) for i in (0, 2, 3)]
            product = Product.find_by_id(self.product_id)
            items = [add_order_product(session, order, product, 1) for order in orders]

            results = [item.can_ship() for item in items]

            for result in results:
                assert not result

    def test_order_item_is_not_shipped(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)

            result = item.is_shipped()

            assert not result

    def test_order_item_is_shipped(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)
            item.shipped_date = date(2020, 9, 1)

            result = item.is_shipped()

            assert result

    def test_order_item_prepare_cancel(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)

            item.prepare_cancel()

            assert item.product.stock == 2

    def test_order_item_fails_to_ship_already_shipped(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)
            item.shipped_date = date(2020, 9, 1)

            with pytest.raises(ModelError):
                item.ship(None)

    def test_order_item_fails_to_ship_with_no_merchant(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)

            with pytest.raises(ModelError):
                item.ship(None)

    def test_order_item_ships_with_valid_merchant(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)

            item.ship(item.product.merchant)

    def test_order_item_fails_to_ship_with_invalid_merchant(self, app):
        with app.app_context():
            item = OrderItem.find_by_id(self.item_id)
            merchant = Merchant.find_by_id(self.other_merchant_id)
            assert merchant is not None

            with pytest.raises(ModelError):
                item.ship(merchant)

def test_order_item_get_items_by_merchant(app, session):
    with app.app_context():
        order = make_order_with_status(session, 1)
        products = [make_product(session, i) for i in range(5)]
        item = add_order_product(session, order, products[0], 1)

        items = OrderItem.find_by_merchant(item.product.merchant).all()

        assert len(items) == 1
        assert items[0].id == item.id
