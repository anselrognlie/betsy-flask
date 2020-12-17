from flask import Blueprint
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
from flask import g

from ..models.product import Product
from ..forms.product_category import Form
from ..logging.logger import logger
from .helper.auth_helper import require_login

bp = Blueprint("product_category", __name__, url_prefix='/products')

@bp.route("/<id>/categories/update", methods=("GET", "POST"))
@require_login
def update(id):  # pylint: disable=redefined-builtin, invalid-name
    product = Product.find_by_id(id)
    if not product:
        flash(f"Could not find product: {id}", "error")
        return redirect(url_for('product.index'))

    if not can_edit(product):
        flash("Merchant does not own this product", "error")
        return redirect(url_for('product.show', id=id))

    return handle_shared_form(product, url_for('product_category.update', id=id),
        'product_category/update.html')

def handle_shared_form(product, form_action, template):
    form = Form(obj=product)

    if form.validate_on_submit():
        params = product_params(form)
        categories = params.get('categories', [])

        try:
            product.update_categories(categories)
            return redirect(url_for('product.show', id=product.id))
        except Exception:  # pylint: disable=broad-except
            msg = 'failed to update categories'
            logger.exception(msg)
            flash(msg, 'error')

    context = dict(
        form=form,
        form_action=form_action
        )

    return render_template(template, **context)

def product_params(form):
    return dict(
        categories=form.categories.data
    )

def can_edit(product):
    return g.session_user.id == product.merchant.id
