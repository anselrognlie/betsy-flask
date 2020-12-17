import pytest

from flask import url_for

from betsy.models.merchant import Merchant
from betsy.models.product import Product
from betsy.models.review import Review
from betsy.logging.logger import logger

from ..test_lib.helpers.flask_helper import assert_flashes, assert_no_flashes, perform_login
from ..test_lib.helpers.model_helpers import (
    make_product
)
from ..test_lib.mocks.mock_attributes import MockAttributes
from ..test_lib.mocks.simple_mocker import SimpleMocker

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

    def test_get_create_review(self):
        with self.app.test_request_context():
            product = Product.find_by_id(self.products_ids[0])

            result = self.client.get(url_for('review.create', product_id=product.id))

            assert result.status_code == 200

    def test_get_create_review_invalid_product(self):
        with self.app.test_request_context():

            result = self.client.get(url_for('review.create', product_id=-1))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(self.client, 'invalid product id', 'error')

    def test_get_create_review_unowned_product(self):
        with self.app.test_request_context():
            merchant = Merchant.find_by_id(self.merchant_ids[0])
            perform_login(self.client, merchant)
            product = Product.find_by_id(self.products_ids[0])

            result = self.client.get(url_for('review.create', product_id=product.id))

            assert result.status_code == 302
            assert result.location.endswith(url_for('page.home'))
            assert_flashes(self.client, 'you cannot review your own product', 'error')

    def test_post_create_product_review(self):
        with self.app.test_request_context():
            product = Product.find_by_id(self.products_ids[0])

            result = self.client.post(url_for('review.create', product_id=product.id),
                data=dict(
                    rating=3,
                    comment='my review'
                ))

            product.reload()
            reviews = product.reviews.all()

            assert result.status_code == 302
            assert result.location.endswith(url_for('product.show', id=product.id))
            assert len(reviews) == 1
            assert reviews[0].rating == 3
            assert reviews[0].comment == 'my review'
            assert_no_flashes(self.client)

    def test_post_create_product_review_fails(self):
        def update_fails(*_args, **_kwargs):
            self.session.rollback()
            raise RuntimeError()

        errors = []
        def my_log(ex):
            errors.append(ex)

        mock = MockAttributes()
        mock.register(Review, 'update', update_fails)
        mock.register(logger, 'exception', my_log)

        with self.app.test_request_context(), SimpleMocker([mock]):
            product = Product.find_by_id(self.products_ids[0])

            result = self.client.post(url_for('review.create', product_id=product.id),
                data=dict(
                    rating=3,
                    comment='my review'
                ))

            product.reload()
            reviews = product.reviews.all()

            assert result.status_code == 200
            assert len(reviews) == 0
            assert_no_flashes(self.client)
