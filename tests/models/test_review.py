import pytest

from betsy.models.review import Review
from betsy.errors.model_error import ModelError

from ..test_lib.helpers.model_helpers import (
    make_product, make_review
)

def test_review_repr(app, session):
    # test that repr gives a nice string
    with app.app_context():
        review = make_review(session, 0)

        debug_str = repr(review)

        assert debug_str == "<Review rating='1'>"

class TestValidation:
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        # pylint: disable=attribute-defined-outside-init
        self.app = app
        self.session = session

    def test_required_review(self):
        with self.app.app_context():
            product = make_product(self.session, 0)
            review = Review(product=product)

            with pytest.raises(ModelError):
                review.save()
