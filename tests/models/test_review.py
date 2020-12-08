from ..test_lib.helpers.model_helpers import (
    make_review
)

def test_review_repr(app, session):
    # test that repr gives a nice string
    with app.app_context():
        review = make_review(session, 0)

        debug_str = repr(review)

        assert debug_str == "<Review rating='1'>"
