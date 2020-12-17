from flask import Blueprint
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for

from ..models.product import Product
from ..forms.product import Form
from ..logging.logger import logger
from .helper.auth_helper import get_current_user, require_login
from .helper.product_helper import can_review, can_edit, can_create

bp = Blueprint("product", __name__, url_prefix='/products')

@bp.route("/")
def index():
    products = Product.available_products()
    context = dict(
        products=products,
        can_create=can_create()
    )

    return render_template('product/index.html', **context)

@bp.route("/<id>")
def show(id):  # pylint: disable=redefined-builtin, invalid-name
    product = Product.find_by_id(id)
    if not product:
        flash(f"Could not find product: {id}", "error")
        return redirect(url_for('product.index'))

    context = dict(
        product=product,
        can_edit=can_edit(product),
        can_review=can_review(product)
    )

    return render_template('product/show.html', **context)

@bp.route("/create", methods=("GET", "POST"))
@require_login
def create():  # pylint: disable=redefined-builtin, invalid-name
    merchant = get_current_user()
    product = Product(merchant=merchant)
    return handle_shared_form(product, url_for('product.create'), 'product/create.html')

@bp.route("/<id>/update", methods=("GET", "POST"))
@require_login
def update(id):  # pylint: disable=redefined-builtin, invalid-name
    product = Product.find_by_id(id)
    if not product:
        flash(f"Could not find product: {id}", "error")
        return redirect(url_for('product.index'))

    if not can_edit(product):
        flash("Merchant does not own this product", "error")
        return redirect(url_for('product.show', id=product.id))

    return handle_shared_form(product, url_for('product.update', id=id), 'product/update.html')

def handle_shared_form(product, form_action, template):
    form = Form(obj=product)

    if form.validate_on_submit():
        try:
            product.update(**product_params(form))
            return redirect(url_for('product.show', id=product.id))
        except Exception:  # pylint: disable=broad-except
            msg = 'failed to update product'
            logger.exception(msg)
            flash(msg, 'error')

    context = dict(
        form=form,
        form_action=form_action,
        merchant=product.merchant
    )

    return render_template(template, **context)

def product_params(form):
    return dict(
        name=form.name.data,
        description=form.description.data,
        photo_url=form.photo_url.data,
        price=form.price.data,
        stock=form.stock.data,
        discontinued=form.discontinued.data
    )
