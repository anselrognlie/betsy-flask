from betsy.models.product import Product
from ..test_lib.helpers.model_helpers import (
    make_category, make_merchant, make_product
)

def test_product_repr(app, session):
    # test that repr gives a nice string
    with app.app_context():
        product = make_product(session, 0)

        debug_str = repr(product)

        assert debug_str == "<Product name='product-0'>"

class TestCategories:
    def test_update_categories(self, app, session):
        with app.app_context():
            product = make_product(session, 0)
            categories = [make_category(session, i) for i in range(5)]

            product.update_categories(categories[:3])
            session.commit()
            product = Product.find_by_id(product.id)

            assert len(product.categories.all()) == 3
            for i, category in enumerate(product.categories):
                assert category.name == f'category-{i}'

def test_unavailable_if_no_stock(app, session):
    with app.app_context():
        product = make_product(session, 0)
        product.stock = 0

        assert not product.is_available()

def test_unavailable_if_discontinued(app, session):
    with app.app_context():
        product = make_product(session, 0)
        product.discontinued = True

        assert not product.is_available()

def test_available_product(app, session):
    with app.app_context():
        product = make_product(session, 0)

        assert product.is_available()

def test_cannot_review_if_discontinued(app, session):
    with app.app_context():
        product = make_product(session, 0)
        product.discontinued = True

        assert not product.can_review(None)

def test_cannot_review_if_owner(app, session):
    with app.app_context():
        product = make_product(session, 0)
        merchant = product.merchant

        assert not product.can_review(merchant)

def test_can_review_if_no_merchant(app, session):
    with app.app_context():
        product = make_product(session, 0)

        assert product.can_review(None)

def test_can_review_if_not_owner(app, session):
    with app.app_context():
        product = make_product(session, 0)
        merchant = make_merchant(session, 1)

        assert product.can_review(merchant)

def test_cannot_review_if_no_merchant(app, session):
    with app.app_context():
        product = make_product(session, 0)

        assert not product.can_edit(None)

def test_cannot_review_if_not_owner(app, session):
    with app.app_context():
        product = make_product(session, 0)
        merchant = make_merchant(session, 1)

        assert not product.can_edit(merchant)

def test_can_review_if_owner(app, session):
    with app.app_context():
        product = make_product(session, 0)

        assert product.can_edit(product.merchant)

def test_get_available_products(app, session):
    with app.app_context():
        products = [make_product(session, i) for i in range(3)]
        products[0].stock = 0
        products[2].discontinued = True
        session.commit()

        available_products = Product.available_products().all()

        assert len(available_products) == 1
        assert available_products[0].id == products[1].id
