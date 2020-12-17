import pytest

from flask import url_for

from betsy.models.merchant import Merchant
from betsy.models.product import Product
from betsy.logging.logger import logger

from ..test_lib.helpers.flask_helper import assert_flashes, assert_no_flashes, perform_login
from ..test_lib.helpers.model_helpers import (
    make_product, make_product_hash
)
from ..test_lib.mocks.simple_mocker import SimpleMocker
from ..test_lib.mocks.mock_attributes import MockAttributes

class TestWithSetup:
    # pylint: disable=no-self-use
    @pytest.fixture(autouse=True)
    def before(self, app, client, session):
        with app.app_context():
            products = [make_product(session, i) for i in range(5)]

            # pylint: disable=attribute-defined-outside-init
            self.app = app
            self.client = client
            self.session = session
            self.products_ids = [product.id for product in products]
            self.merchant_ids = [product.merchant.id for product in products]

    def perform_login(self):
        # with self.app.test_request_context():
        merchant = Merchant.find_by_id(self.merchant_ids[0])
        perform_login(self.client, merchant)
        return merchant

    def test_index(self):
        with self.app.test_request_context():
            assert self.client.get(url_for('product.index')).status_code == 200

    def test_show_product(self):
        with self.app.test_request_context():
            result = self.client.get(url_for('product.show', id=self.products_ids[0]))

            assert result.status_code == 200

    def test_show_invalid_product(self):
        with self.app.test_request_context():
            result = self.client.get(url_for('product.show', id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('product.index'))
            assert_flashes(self.client, 'Could not find product: -1', 'error')

    def test_get_create_product(self):
        with self.app.test_request_context():
            merchant = Merchant.find_by_id(self.merchant_ids[0])
            perform_login(self.client, merchant)

            result = self.client.get(url_for('product.create'))

            assert result.status_code == 200

    def test_get_update_product(self):
        with self.app.test_request_context():
            product = Product.find_by_id(self.products_ids[0])
            merchant = product.merchant
            perform_login(self.client, merchant)

            result = self.client.get(url_for('product.update', id=product.id))

            assert result.status_code == 200

    def test_get_update_invalid_product(self):
        with self.app.test_request_context():
            merchant = Merchant.find_by_id(self.merchant_ids[0])
            perform_login(self.client, merchant)

            result = self.client.get(url_for('product.update', id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('product.index'))
            assert_flashes(self.client, 'Could not find product: -1', 'error')

    def test_get_update_unowned_product(self):
        with self.app.test_request_context():
            merchant = Merchant.find_by_id(self.merchant_ids[0])
            perform_login(self.client, merchant)
            product = Product.find_by_id(self.products_ids[1])

            result = self.client.get(url_for('product.update', id=product.id))

            assert result.status_code == 302
            assert result.location.endswith(url_for('product.show', id=product.id))
            assert_flashes(self.client, 'Merchant does not own this product', 'error')

    def test_post_create_product(self):
        with self.app.test_request_context():
            merchant = Merchant.find_by_id(self.merchant_ids[0])
            perform_login(self.client, merchant)

            product_hash = make_product_hash(6)
            result = self.client.post(url_for('product.create'), data=product_hash)

            product = Product.query.filter(Product.name == product_hash['name']).first()

            assert result.status_code == 302
            assert result.location.endswith(url_for('product.show', id=product.id))
            assert product.name == product_hash['name']
            assert_no_flashes(self.client)

    def test_post_update_product(self):
        with self.app.test_request_context():
            product = Product.find_by_id(self.products_ids[0])
            merchant = product.merchant
            perform_login(self.client, merchant)

            product_hash = make_product_hash(6)
            result = self.client.post(url_for('product.update', id=product.id),
                data=product_hash)

            self.session.refresh(product)

            assert result.status_code == 302
            assert result.location.endswith(url_for('product.show', id=product.id))
            assert product.name == product_hash['name']
            assert_no_flashes(self.client)

    def test_post_update_product_invalid_price(self):
        with self.app.test_request_context():
            product = Product.find_by_id(self.products_ids[0])
            merchant = product.merchant
            perform_login(self.client, merchant)

            product_hash = make_product_hash(6)
            product_hash['price'] = 'invalid'
            result = self.client.post(url_for('product.update', id=product.id),
                data=product_hash)

            self.session.refresh(product)

            assert result.status_code == 200
            assert_no_flashes(self.client)

    def test_post_update_product_no_price(self):
        with self.app.test_request_context():
            product = Product.find_by_id(self.products_ids[0])
            merchant = product.merchant
            perform_login(self.client, merchant)

            product_hash = make_product_hash(6)
            del product_hash['price']
            result = self.client.post(url_for('product.update', id=product.id),
                data=product_hash)

            self.session.refresh(product)

            assert result.status_code == 200
            assert_no_flashes(self.client)

    def test_post_update_product_fails(self):
        def update_fails(*args, **kwargs):
            raise RuntimeError()

        errors = []
        def my_log(ex):
            errors.append(ex)

        mock = MockAttributes()
        mock.register(Product, 'update', update_fails)
        mock.register(logger, 'exception', my_log)

        with self.app.test_request_context(), SimpleMocker([mock]):
            product = Product.find_by_id(self.products_ids[0])
            merchant = product.merchant
            perform_login(self.client, merchant)

            product_hash = make_product_hash(6)
            result = self.client.post(url_for('product.update', id=product.id),
                data=product_hash)

            self.session.refresh(product)

            assert result.status_code == 200
            assert product.name == 'product-0'
            assert_no_flashes(self.client)
            assert str(errors[0]) == 'failed to update product'
