from flask import Blueprint
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for

from ..forms.review import Form
from ..models.review import Review
from ..models.product import Product
from ..logging.logger import logger
from .helper.route_helper import redirect_home
from .helper.product_helper import can_review

bp = Blueprint("review", __name__, url_prefix='/reviews')

@bp.route("/for_product/<product_id>/create", methods=("GET", "POST"))
def create(product_id):  # pylint: disable=redefined-builtin, invalid-name
    product = Product.find_by_id(product_id)

    if product is None:
        flash("invalid product id", "error")
        return redirect_home()

    if not can_review(product):
        flash("you cannot review your own product", "error")
        return redirect_home()

    review = Review(product=product)
    return handle_shared_form(
        review,
        url_for('review.create', product_id=product_id),
        'review/create.html'
        )

def handle_shared_form(review, form_action, template):
    form = Form(obj=review)

    if form.validate_on_submit():
        try:
            review.update(**review_params(form))
            return redirect(url_for('product.show', id=review.product.id))

        except Exception:  # pylint: disable=broad-except
            msg = 'failed to save review'
            flash(msg, 'error')
            logger.exception(msg)

    context = dict(
        form=form,
        form_action=form_action,
        product=review.product
        )

    return render_template(template, **context)

def review_params(form):
    return dict(
        rating=form.rating.data,
        comment=form.comment.data
    )
