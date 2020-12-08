from .auth_helper import get_current_user, is_logged_in

def can_review(product):
    session_user = get_current_user()
    return product.can_review(session_user)

def can_edit(product):
    session_user = get_current_user()
    return product.can_edit(session_user)

def can_create():
    return is_logged_in()
