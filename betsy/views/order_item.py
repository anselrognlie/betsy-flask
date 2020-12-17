# pylint: disable=missing-module-docstring

from flask import Blueprint
from flask import redirect
from flask import url_for
from flask import flash

from ..logging.logger import logger
from ..models.order_item import OrderItem
from .helper.auth_helper import get_current_user, require_login

bp = Blueprint("order_item", __name__, url_prefix="/order_items")

@bp.route('/<id>/delete', methods=('POST',))
def delete(id):  # pylint: disable=invalid-name, redefined-builtin
    err_msg = None

    item = OrderItem.find_by_id(id)
    if item is None:
        err_msg = "Could not update order"
    else:
        try:
            item.delete()

        except Exception:  # pylint: disable=broad-except
            err_msg = 'Failed to delete order item'
            logger.exception(err_msg)

    if err_msg:
        flash(err_msg, 'error')

    return redirect(url_for('order.cart'))

@bp.route('/<id>/ship', methods=('POST',))
@require_login
def ship(id):  # pylint: disable=invalid-name, redefined-builtin
    err_msg = None

    item = OrderItem.find_by_id(id)
    if item is None:
        err_msg = "Could not ship order"
    else:
        try:
            item.ship(get_current_user())

        except Exception:  # pylint: disable=broad-except
            err_msg = 'Failed to ship order item'
            logger.exception(err_msg)

    if err_msg:
        flash(err_msg, 'error')

    return redirect(url_for('merchant.orders'))
