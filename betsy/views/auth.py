from flask import Blueprint
from flask import request
from flask import url_for
from flask import flash
from flask import redirect

from ..models.merchant import Merchant
from ..auth.github import github
from ..auth.github_auth import github_auth
from .helper.session_helper import set_logged_in_user_id

bp = Blueprint("auth", __name__, url_prefix="/auth/github")

@bp.route('/', methods=('POST',))
def login():
    return github.authorize(scope='user:email')

@bp.route('/callback')
@github.authorized_handler
@github_auth.auth_hash_sink
def authorized(auth_hash):
    next_url = request.args.get('next') or url_for('page.home')

    user = Merchant.make_from_auth_hash(auth_hash)

    if not auth_hash or not user:
        flash("Authorization failed.")
        return redirect(next_url)

    set_logged_in_user_id(user)
    flash(f"Logged in user: {user.name}")

    return redirect(next_url)
