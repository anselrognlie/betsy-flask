import pytest
from datetime import datetime

from betsy.errors.model_error import ModelError
from betsy.models.order import Order
from betsy.models.order_status import OrderStatus
from betsy.models.product import Product
from betsy.models.merchant import Merchant

from ..test_lib.helpers.model_helpers import (
    add_order_product, make_order, make_merchant, make_product, make_checkout_kwargs,
    make_order_with_status
)
from ..test_lib.mocks.simple_mocker import SimpleMocker
from ..test_lib.mocks.mock_now import MockNow

def test_order_repr(app, session):
    with app.app_context():
        # test that repr gives a nice string
        order = make_order(session, 1)
        debug_str = repr(order)
        assert debug_str == "<Order email='email-1@email.com'>"

def test_make_cart(app):
    with app.app_context():
        cart = Order.make_cart()

        assert cart.status == 'pending'
        assert cart.order_items.count() == 0

class TestSimpleSubtotal:
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        with app.app_context():
            cart = Order.make_cart()
            merchant = make_merchant(session, 1)
            products = [make_product(session, i, merchant) for i in range(5)]

            add_order_product(session, cart, products[0], 1)
            add_order_product(session, cart, products[1], 2)

            # pylint: disable=attribute-defined-outside-init
            self.order_id = cart.id
            self.product_id = products[0].id

    def test_order_subtotal(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)

            total = order.total()
            assert (1000 * 1 + 2000 * 2) == total

    def test_find_order_by_product(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            product = Product.find_by_id(self.product_id)

            item = order.find_item_by_product(product)

            assert product.id == item.product_id
            assert item.quantity == 1

class TestAddProduct:
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        with app.app_context():
            cart = Order.make_cart()
            products = [make_product(session, i) for i in range(2)]

            products[0].stock = 10
            add_order_product(session, cart, products[0], 5)

            # pylint: disable=attribute-defined-outside-init
            self.order_id = cart.id
            self.product_ids = [product.id for product in products]

    def test_add_new_product_to_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            product = Product.find_by_id(self.product_ids[1])

            order.add_product(product, 1)

            expected_quantities = {
                self.product_ids[0]: 5,
                self.product_ids[1]: 1
            }

            items = order.order_items.all()
            assert len(items) == 2
            for item in items:
                assert expected_quantities[item.product_id] == item.quantity

    def test_add_existing_product_to_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            product = Product.find_by_id(self.product_ids[0])

            order.add_product(product, 1)

            expected_quantities = {
                self.product_ids[0]: 6,
            }

            items = order.order_items.all()
            assert len(items) == 1
            for item in items:
                assert expected_quantities[item.product_id] == item.quantity

    def test_add_insufficient_product_to_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            product = Product.find_by_id(self.product_ids[1])

            with pytest.raises(ModelError):
                order.add_product(product, 3)

    def test_update_new_product_to_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            product = Product.find_by_id(self.product_ids[1])

            with pytest.raises(ModelError):
                order.update_product(product, 1)

    def test_update_existing_product_to_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            product = Product.find_by_id(self.product_ids[0])

            order.update_product(product, 3)

            expected_quantities = {
                self.product_ids[0]: 3,
            }

            items = order.order_items.all()
            assert len(items) == 1
            for item in items:
                assert expected_quantities[item.product_id] == item.quantity

    def test_update_insufficient_product_to_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            product = Product.find_by_id(self.product_ids[0])

            with pytest.raises(ModelError):
                order.update_product(product, 11)

    def test_update_invalid_quantity_to_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            product = Product.find_by_id(self.product_ids[0])

            with pytest.raises(ModelError):
                order.update_product(product, -1)

    def test_update_zero_quantity_in_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            product = Product.find_by_id(self.product_ids[0])

            order.update_product(product, 0)

            items = order.order_items.all()
            assert len(items) == 0

class TestFilterOrderItems:
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        with app.app_context():
            order = make_order(session, 0)
            products = [make_product(session, i) for i in range(3)]

            add_order_product(session, order, products[0], 2)
            add_order_product(session, order, products[1], 3)

            # pylint: disable=attribute-defined-outside-init
            self.order_id = order.id
            self.product_id = products[0].id
            self.merchant_id = products[0].merchant_id

    def test_order_items_for_merchant(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            merchant = Merchant.find_by_id(self.merchant_id)

            items = order.items_for_merchant(merchant).all()

            assert len(items) == 1
            assert items[0].product_id == self.product_id

class TestCanCheckout:
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        with app.app_context():
            cart = Order.make_cart()

            products = [make_product(session, i) for i in range(2)]

            products[0].stock = 5
            add_order_product(session, cart, products[0], 7)

            # pylint: disable=attribute-defined-outside-init
            self.cart_id = cart.id
            self.product_ids = [product.id for product in products]

    def test_cannot_checkout_non_pending_order(self, app, session):
        with app.app_context():
            orders = [make_order_with_status(session, i) for i in range(1, 3 + 1)]

            results = [order.can_checkout() for order in orders]

            for result in results:
                assert not result

    def test_cannot_checkout_empty_order(self, app):
        with app.app_context():
            order = Order.make_cart()

            result = order.can_checkout()

            assert not result

    def test_cannot_checkout_invalid_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.cart_id)

            result = order.can_checkout()

            assert not result

    def test_can_checkout_valid_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.cart_id)
            product = Product.find_by_id(self.product_ids[0])

            order.update_product(product, 5)

            result = order.can_checkout()

            assert result

class TestCheckout:
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        with app.app_context():
            cart = Order.make_cart()

            products = [make_product(session, i) for i in range(5)]

            products[0].stock = 5
            add_order_product(session, cart, products[0], 5)

            # pylint: disable=attribute-defined-outside-init
            self.cart_id = cart.id
            self.product_ids = [product.id for product in products]

    def test_cannot_checkout_invalid_order(self, app):
        with app.app_context():
            order = Order.make_cart()

            with pytest.raises(ModelError):
                order.checkout()

    def test_can_checkout_valid_order(self, app):
        with app.app_context(), SimpleMocker([MockNow(datetime(2020, 9, 1))]):
            order = Order.find_by_id(self.cart_id)

            order.checkout(**make_checkout_kwargs(1))

            product = Product.find_by_id(self.product_ids[0])
            assert product.stock == 0
            assert order.status == 'paid'
            assert order.email == 'email-1@email.com'
            assert order.ordered_date == datetime(2020, 9, 1)

class TestCancelAndCompletion:
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        with app.app_context():
            order = make_order(session, 0)
            order.status = 'paid'

            products = [make_product(session, i) for i in range(2)]

            items = [add_order_product(session, order, product, i + 1)
                for i, product in enumerate(products)]

            # pylint: disable=attribute-defined-outside-init
            self.order_id = order.id
            self.item_ids = [item.id for item in items]

    def test_cannot_cancel_non_paid_order(self, app, session):
        with app.app_context():
            orders = [make_order_with_status(session, i) for i in (0, 2, 3)]

            results = [order.can_cancel() for order in orders]

            for result in results:
                assert not result

    def test_can_cancel_non_shipped_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)

            result = order.can_cancel()

            assert result

    def test_cannot_cancel_shipped_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            item = order.order_items[0]
            item.ship(item.product.merchant)

            result = order.can_cancel()

            assert not result

    def test_cancel_non_shipped_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)

            order.cancel()

            assert order.status == OrderStatus.CANCELLED.value

    def test_cancel_noncancellable_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            item = order.order_items[0]
            item.ship(item.product.merchant)

            with pytest.raises(ModelError):
                order.cancel()

            assert order.status == OrderStatus.PAID.value

    def test_refresh_incomplete_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)

            order.refresh_status()

            assert order.status == OrderStatus.PAID.value

    def test_refresh_non_paid_order(self, app, session):
        with app.app_context():
            orders = [make_order_with_status(session, i) for i in (0, 2, 3)]

            def refresh_and_get_status(order):
                order.refresh_status()
                return order.status

            results = [refresh_and_get_status(order) for order in orders]

            for i, order in enumerate(orders):
                result = results[i]
                assert result == order.status

    def test_refresh_complete_order(self, app):
        with app.app_context():
            order = Order.find_by_id(self.order_id)
            for item in order.order_items:
                item.shipped_date = datetime(2020, 9, 1)

            order.refresh_status()

            assert order.status == OrderStatus.COMPLETED.value
