from flask import session

from ...keys import LOGGED_IN_USER_ID, CART_ID

def set_logged_in_user_id(merchant):
    user_id = None
    if merchant:
        user_id = merchant.id if hasattr(merchant, 'id') else merchant

    session[LOGGED_IN_USER_ID] = user_id

def get_logged_in_user_id():
    return session.get(LOGGED_IN_USER_ID)

def set_cart_id(order):
    order_id = None
    if order:
        order_id = order.id if hasattr(order, 'id') else order

    session[CART_ID] = order_id

def get_cart_id():
    return session.get(CART_ID)
