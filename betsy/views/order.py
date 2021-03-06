# pylint: disable=missing-module-docstring

import flask
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request

from ..models.order import Order
from ..models.product import Product
from ..forms.order import Form
from ..logging.logger import logger
from .helper.auth_helper import require_login
from .helper.session_helper import get_cart_id, set_cart_id
from .helper.auth_helper import get_current_user
from .helper.order_helper import require_cart
from .helper.order_helper import get_cart, set_cart
from .helper.error_helper import flash_errors

bp = Blueprint("order", __name__, url_prefix="/orders")

@bp.before_app_request
def ensure_cart():
    cart = Order.find_by_id(get_cart_id())  # pylint: disable=redefined-outer-name
    if cart is None:
        cart = Order.make_cart()

    set_cart_id(cart)
    set_cart(cart)

@bp.app_context_processor
def add_cart_to_context():
    return dict(
        cart=get_cart()
    )

@bp.route('/cart')
@require_cart
def cart():
    cart = get_cart()  # pylint: disable=redefined-outer-name
    order_items = cart.order_items.all()
    context = dict(
        order=cart,
        order_items=order_items
    )

    return render_template('order/cart.html', **context)

@bp.route('/add_product/<product_id>', methods=('POST',))
@require_cart
def add_product(product_id):
    cart = get_cart()  # pylint: disable=redefined-outer-name
    product = Product.find_by_id(product_id)
    if product is None:
        flask.flash(f"Could not find product: {product_id}", "error")
        return redirect(url_for('product.index'))

    quantity = int(request.form.get('quantity'))
    try:
        cart.add_product(product, quantity)
    except Exception:  # pylint: disable=broad-except
        msg = "Could not add requested product quantity"
        flask.flash(msg, "error")
        logger.exception(msg)
        return redirect(url_for('product.show', id=product_id))

    return redirect(url_for('order.cart'))

@bp.route('/update_product/<product_id>', methods=('POST',))
@require_cart
def update_product(product_id):
    cart = get_cart()  # pylint: disable=redefined-outer-name
    product = Product.find_by_id(product_id)
    if product is None:
        flask.flash(f"Could not find product: {product_id}", "error")
        return redirect(url_for('product.index'))

    quantity = int(request.form.get('quantity'))
    try:
        cart.update_product(product, quantity)
    except Exception:  # pylint: disable=broad-except
        msg = "Could not update requested product quantity"
        flask.flash(msg, "error")
        logger.exception(msg)
        return redirect(url_for('product.show', id=product_id))

    return redirect(url_for('order.cart'))

@bp.route('/checkout', methods=('GET', 'POST'))
@require_cart
def checkout():
    cart = get_cart()  # pylint: disable=redefined-outer-name
    if not cart.can_checkout():
        flask.flash('Unable to process checkout', 'error')
        return redirect(url_for('order.cart'))

    form = Form(obj=cart)

    if form.validate_on_submit():
        try:
            cart.checkout(**order_params(form))
            set_cart_id(None)
            return redirect(url_for('order.show', id=cart.id))
        except Exception:  # pylint: disable=broad-except
            msg = "Unable to complete checkout"
            flask.flash(msg, "error")
            logger.exception(msg)
            flash_errors(cart.errors)

    context = dict(
        form=form,
        form_action=url_for('order.checkout'),
        order=cart,
        order_items=cart.order_items
    )

    return render_template('order/checkout.html', **context)

@bp.route('/<id>')
def show(id):  # pylint: disable=invalid-name, redefined-builtin
    order = Order.find_by_id(id)
    if not order:
        flask.flash('Invalid order', 'error')
        return redirect(url_for('page.home'))

    context = dict(
        order=order,
        order_items=order.order_items.all()
    )

    return render_template('order/show.html', **context)

@bp.route('/<id>/cancel', methods=('POST',))
def cancel(id):  # pylint: disable=invalid-name, redefined-builtin
    order = Order.find_by_id(id)
    if not order:
        flask.flash('Invalid order', 'error')
        return redirect(url_for('page.home'))

    try:
        order.cancel()
    except Exception:  # pylint: disable=broad-except
        msg = 'Unable to cancel order'
        logger.exception(msg)
        flask.flash(msg, 'error')

    return redirect(url_for('order.show', id=id))

@bp.route('/<id>/details')
@require_login
def details(id):  # pylint: disable=invalid-name, redefined-builtin
    order = Order.find_by_id(id)
    if not order:
        flask.flash('Invalid order', 'error')
        return redirect(url_for('page.home'))

    context = dict(
        order=order,
        order_items=order.items_for_merchant(get_current_user()).all()
    )

    return render_template('order/details.html', **context)

def order_params(form):
    return dict(
        email=form.email.data,
        mailing_address=form.mailing_address.data,
        cc_name=form.cc_name.data,
        cc_number=form.cc_number.data,
        cc_exp=form.cc_exp.data,
        cc_cvv=form.cc_cvv.data,
        cc_zipcode=form.cc_zipcode.data
    )
