import pytest
import re

from betsy.errors.model_error import ModelError
from betsy.models.merchant import Merchant
from betsy.models.order_status import OrderStatus
from betsy.models.order import Order
from betsy.models.product import Product

from ..test_lib.helpers.model_helpers import (
    make_merchant, make_product, make_order, add_order_product
)

def cmp_revenue_summary(expected, result):
    # pylint: disable=multiple-statements
    if len(expected) != len(result): return False

    for status, expected_record in expected.items():
        if status not in result: return False

        result_record = result.get(status)
        if expected_record['count'] != result_record.count: return False
        if expected_record['total'] != result_record.total: return False

    return True

def cmp_order_summary(expected, result):
    # pylint: disable=multiple-statements
    if len(expected) != len(result): return False

    for status, expected_record in expected.items():
        if status not in result: return False

        result_record = result.get(status)
        if len(expected_record) != len(result_record): return False

        for order_id, expected_order_detail in expected_record.items():
            if order_id not in result_record: return False

            result_order_detail = result_record[order_id]
            if expected_order_detail['order'] != result_order_detail.order.id: return False

            expected_items = expected_order_detail['items']
            result_items = result_order_detail.items
            if len(expected_items) != len(result_items): return False

            for i, expected_item in enumerate(expected_items):
                result_item = result_items[i]
                if expected_item != result_item.id: return False

    return True

def test_merchant_repr():
    # test that repr gives a nice string
    merchant = Merchant(
        name='merchant',
        email='email',
        provider='sample',
        uid='uid'
    )
    debug_str = repr(merchant)
    assert debug_str == "<Merchant name='merchant'>"

class TestFindMerchantsByProvider:
    # pylint: disable=no-self-use
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        with app.app_context():
            merchants = [make_merchant(session, i) for i in range(5)]

            merchants[0].provider = 'provider'
            merchants[1].provider = 'provider'
            session.commit()

    def test_find_merchants_by_provider(self, app):
        with app.app_context():
            merchant = Merchant.find_by_provider_uid('provider', 1)

            assert merchant is not None
            assert merchant.name == 'merchant-1'

class TestMerchantProducts:
    # pylint: disable=no-self-use
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        with app.app_context():
            merchant = make_merchant(session, 1)
            products = [make_product(session, i, merchant) for i in range(5)]
            orders = [make_order(session, i) for i in range(4)]

            statuses = OrderStatus.all()
            items = []
            for i, order in enumerate(orders):
                # pending has 1 product 0 (1000 * 1)
                # paid has 2 product 1 (2000 * 2)
                # complete has 3 product 0 (1000 * 3)
                # cancelled has 4 product 1 (2000 * 4)
                status = statuses[i]
                order.status = status
                item = add_order_product(session, order, products[i % 2], i + 1)
                items.append(item.id)

            products[3].discontinued = True
            products[4].stock = 0
            session.commit()

            # pylint: disable=attribute-defined-outside-init
            self.merchant_id = merchant.id
            self.orders = [order.id for order in orders]
            self.items = items

    def test_available_products_for_merchant(self, app):
        with app.app_context():
            merchant = Merchant.find_by_id(self.merchant_id)
            products = merchant.available_products().all()

            assert len(products) == 3

    def test_merchant_total_revenue(self, app):
        with app.app_context():
            merchant = Merchant.find_by_id(self.merchant_id)
            revenue = merchant.total_revenue()

            assert revenue == (2000 * 2 + 1000 * 3)

    def test_merchant_status_revenue(self, app):
        with app.app_context():
            subtotals = [1000, 4000, 3000, 8000]

            statuses = OrderStatus.all()
            merchant = Merchant.find_by_id(self.merchant_id)
            results = [merchant.revenue_by_status(status) for status in statuses]

            assert subtotals == results

    def test_merchant_revenue_summary(self, app):
        with app.app_context():
            expected = dict(
                pending=dict(count=1, total=1000),
                paid=dict(count=1, total=4000),
                completed=dict(count=1, total=3000),
                cancelled=dict(count=1, total=8000)
            )

            merchant = Merchant.find_by_id(self.merchant_id)
            result = merchant.revenue_summary()

            assert cmp_revenue_summary(expected, result)

    def test_merchant_revenue_summary_no_pending(self, app, session):
        with app.app_context():
            expected = dict(
                pending=dict(count=0, total=0),
                paid=dict(count=1, total=4000),
                completed=dict(count=1, total=3000),
                cancelled=dict(count=2, total=9000)
            )

            merchant = Merchant.find_by_id(self.merchant_id)
            order = Order.query.filter(Order.status == 'pending').first()
            order.status = 'cancelled'
            session.commit()

            result = merchant.revenue_summary()

            assert cmp_revenue_summary(expected, result)

    def test_merchant_order_summary(self, app):
        with app.app_context():
            expected = dict(
                pending={self.orders[0]: dict(order=self.orders[0], items=[self.items[0]])},
                paid={self.orders[1]: dict(order=self.orders[1], items=[self.items[1]])},
                completed={self.orders[2]: dict(order=self.orders[2], items=[self.items[2]])},
                cancelled={self.orders[3]: dict(order=self.orders[3], items=[self.items[3]])}
            )

            merchant = Merchant.find_by_id(self.merchant_id)
            result = merchant.orders_summary()

            assert cmp_order_summary(expected, result)

    def test_merchant_order_summary_no_pending(self, app, session):
        with app.app_context():

            merchant = Merchant.find_by_id(self.merchant_id)
            product = Product.find_by_id(2)
            order = Order.query.filter(Order.status == 'pending').first()
            order.status = 'cancelled'
            item = add_order_product(session, order, product, 1)
            session.commit()

            expected = dict(
                paid={self.orders[1]: dict(order=self.orders[1], items=[self.items[1]])},
                completed={self.orders[2]: dict(order=self.orders[2], items=[self.items[2]])},
                cancelled={
                    self.orders[3]: dict(order=self.orders[3], items=[self.items[3]]),
                    self.orders[0]: dict(order=self.orders[0], items=[self.items[0], item.id])
                }
            )

            result = merchant.orders_summary()

            assert cmp_order_summary(expected, result)

def test_make_new_merchant_from_auth(app):
    with app.app_context():
        auth_hash = dict(
            uid='uid',
            email='uid@email.com',
            name='UID',
            provider='github'
        )

        merchant = Merchant.make_from_auth_hash(auth_hash)

        assert Merchant.query.count() == 1
        assert merchant.uid == 'uid'
        assert merchant.email == 'uid@email.com'
        assert merchant.name == 'UID'
        assert merchant.provider == 'github'

def test_make_existing_merchant_from_auth(app, session):
    with app.app_context():
        auth_hash = dict(
            uid='uid',
            email='uid@email.com',
            name='UID',
            provider='github'
        )
        regular_merchant = Merchant(**auth_hash)
        session.add(regular_merchant)
        session.commit()

        assert Merchant.query.count() == 1

        merchant = Merchant.make_from_auth_hash(auth_hash)

        assert Merchant.query.count() == 1
        assert merchant.uid == 'uid'
        assert merchant.email == 'uid@email.com'
        assert merchant.name == 'UID'
        assert merchant.provider == 'github'

def test_make_invalid_merchant_from_auth(app):
    with app.app_context():
        auth_hash = dict()

        merchant = Merchant.make_from_auth_hash(auth_hash) # pylint: disable=protected-access

        assert Merchant.query.count() == 0
        assert not merchant

def test_invalid_internal_merchant_from_auth(app):
    with app.app_context():
        auth_hash = dict()

        with pytest.raises(ModelError):
            Merchant._make_user_internal(auth_hash) # pylint: disable=protected-access

        assert Merchant.query.count() == 0

def test_unique_validation(app, session):
    with app.app_context():
        original = make_merchant(session, 0)
        merchant = make_merchant(session, 1)
        merchant.email = original.email

        with pytest.raises(ModelError):
            merchant.save()

        assert re.search(r'email', merchant.errors[0].field)
        assert re.search(r'unique', merchant.errors[0].message)

def test_required_validation(app):
    with app.app_context():
        for field in ('name', 'provider', 'uid'):
            merchant = Merchant(
                name='n', email='address@domain.com', provider='p', uid='u'
            )
            setattr(merchant, field, None)

            with pytest.raises(ModelError):
                merchant.save()

            assert re.search(field, merchant.errors[0].field)
            assert re.search(r'required', merchant.errors[0].message)

def test_email_required_validation(app):
    with app.app_context():
        merchant = Merchant(
            name='n', provider='p', uid='u'
        )

        with pytest.raises(ModelError):
            merchant.save()

        # look for matches in errors collection
        found_error = None
        for error in merchant.errors:
            if re.search(r'required', error.message):
                found_error = error
                break

        assert re.search(r'email', found_error.field)

def test_email_validation(app):
    with app.app_context():
        merchant = Merchant(
            name='n', email='invalid', provider='p', uid='u'
        )

        with pytest.raises(ModelError):
            merchant.save()

        assert re.search(r'email', merchant.errors[0].field)
        assert re.search(r'valid', merchant.errors[0].message)
