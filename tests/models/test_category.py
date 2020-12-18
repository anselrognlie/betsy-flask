from betsy.errors.model_error import ModelError
import pytest

from betsy.models.category import Category

from ..test_lib.helpers.model_helpers import make_category, make_product

def test_category_repr():
    # test that repr gives a nice string
    category = Category(name='category')
    debug_str = repr(category)
    assert debug_str == "<Category name='category'>"

class TestCategoryWithProducts:
    # pylint: disable=no-self-use
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        with app.app_context():
            products = [make_product(session, i) for i in range(5)]
            category = make_category(session, 1)

            for product in products:
                product.categories.append(category)

            products[1].discontinued = True
            products[4].stock = 0
            session.commit()

    def test_available_products_for_category(self, app):
        with app.app_context():
            category = Category.query.first()
            products = category.available_products().all()

            assert len(products) == 3

    def test_unique_validation(self, app):
        with app.app_context():
            category = Category.query.first()

            with pytest.raises(ModelError):
                Category(name=category.name).save()
