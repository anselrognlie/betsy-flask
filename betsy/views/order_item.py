# pylint: disable=missing-module-docstring

from flask import Blueprint
from flask import redirect
from flask import url_for
from flask import flash

from ..models.order_item import OrderItem
from .helper.auth_helper import get_current_user, require_login

bp = Blueprint("order_item", __name__, url_prefix="/order_items")

@bp.route('/<id>/delete', methods=('POST',))
def delete(id):  # pylint: disable=invalid-name, redefined-builtin
    item = OrderItem.find_by_id(id)
    if item is None or not item.destroy():
        flash("Could not update order", "error")

    return redirect(url_for('order.cart'))

@bp.route('/<id>/ship', methods=('POST',))
@require_login
def ship(id):  # pylint: disable=invalid-name, redefined-builtin
    item = OrderItem.find_by_id(id)
    if item is None or not item.ship(get_current_user()):
        flash("Could not ship order", "error")

    return redirect(url_for('merchant.orders'))
