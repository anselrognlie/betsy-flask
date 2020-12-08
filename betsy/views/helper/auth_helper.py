import functools

from flask import redirect
from flask import url_for
from flask import flash
from flask import g

def require_login(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.logged_in:
            flash("This feature requires being logged in", "error")
            return redirect(url_for("page.home"))

        return view(**kwargs)

    return wrapped_view

def is_logged_in():
    return g.logged_in

def get_current_user():
    return g.session_user
