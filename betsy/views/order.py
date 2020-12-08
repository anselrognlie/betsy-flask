# pylint: disable=missing-module-docstring

from betsy.views.helper.auth_helper import require_login
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash
from flask import request

from ..models.order import Order
from ..models.product import Product
from ..forms.order import Form
from .helper.session_helper import get_cart_id, set_cart_id
from .helper.auth_helper import get_current_user
from .helper.order_helper import require_cart
from .helper.order_helper import get_cart, set_cart

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
        flash(f"Could not find product: {product_id}", "error")
        return redirect(url_for('product.index'))

    quantity = int(request.form.get('quantity'))
    if not cart.add_product(product, quantity):
        flash("Could not add requested product quantity", "error")
        return redirect(url_for('product.show', id=product_id))

    return redirect(url_for('order.cart'))

@bp.route('/update_product/<product_id>', methods=('POST',))
@require_cart
def update_product(product_id):
    cart = get_cart()  # pylint: disable=redefined-outer-name
    product = Product.find_by_id(product_id)
    if product is None:
        flash(f"Could not find product: {product_id}", "error")
        return redirect(url_for('product.index'))

    quantity = int(request.form.get('quantity'))
    if not cart.update_product(product, quantity):
        flash("Could not update requested product quantity", "error")
        return redirect(url_for('product.show', id=product_id))

    return redirect(url_for('order.cart'))

@bp.route('/checkout', methods=('GET', 'POST'))
@require_cart
def checkout():
    cart = get_cart()  # pylint: disable=redefined-outer-name
    if not cart.can_checkout():
        flash('Unable to process checkout', 'error')
        return redirect(url_for('order.cart'))

    form = Form(obj=cart)

    if form.validate_on_submit():
        if cart.checkout(**order_params(form)):
            set_cart_id(None)
            return redirect(url_for('order.show', id=cart.id))
        else:
            flash('Unable to complete checkout', 'error')

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
        flash('Invalid order', 'error')
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
        flash('Invalid order', 'error')
        return redirect(url_for('page.home'))

    if not order.cancel():
        flash('Unable to cancel order', 'error')

    return redirect(url_for('order.show', id=id))

@bp.route('/<id>/details')
@require_login
def details(id):  # pylint: disable=invalid-name, redefined-builtin
    order = Order.find_by_id(id)
    if not order:
        flash('Invalid order', 'error')
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
