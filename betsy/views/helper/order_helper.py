import functools

from flask import redirect
from flask import url_for
from flask import flash
from flask import g

def require_cart(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if get_cart() is None:
            flash("Unable to create cart", "error")
            return redirect(url_for("page.home"))

        return view(**kwargs)

    return wrapped_view

def get_cart():
    return g.cart

def set_cart(cart):
    g.cart = cart
