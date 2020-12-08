# pylint: disable=missing-module-docstring

from betsy.models.order_status import OrderStatus
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash
from flask import current_app
from flask import g

from ..models.merchant import Merchant
from ..dao.builder.merchant_dao_builder import MerchantDaoBuilder
from ..keys import ALLOW_IMPERSONATION
from ..forms.merchant import Form
from ..storage.db import db
from .helper.session_helper import get_logged_in_user_id, set_logged_in_user_id
from .helper.auth_helper import get_current_user, require_login

bp = Blueprint("merchant", __name__, url_prefix="/merchants")

def get_merchant_dao_builder():
    return g.merchant_dao_builder

@bp.before_app_request
def load_session_user():
    g.session_user = Merchant.find_by_id(get_logged_in_user_id())
    g.logged_in = g.session_user is not None
    g.allow_impersonation = current_app.config.get(ALLOW_IMPERSONATION, False)
    g.merchant_dao_builder = MerchantDaoBuilder(g.allow_impersonation)

@bp.route("/")
def index():
    merchants = Merchant.query.order_by(Merchant.name)
    builder = get_merchant_dao_builder()
    context = dict(
        merchants=(builder.build(merchant) for merchant in merchants)
    )

    return render_template("merchant/index.html", **context)

@bp.route("/<id>/impersonate", methods=("POST",))
def impersonate(id):  # pylint: disable=redefined-builtin, invalid-name
    if not g.allow_impersonation:
        return redirect(url_for('page.home'))

    merchant = Merchant.query.filter(Merchant.id == id).first()
    if merchant:
        flash(f"Impersonating user: {merchant.name}", "success")
        set_logged_in_user_id(id)
    else:
        flash(f"Could not find user: {id}", "error")

    return redirect(url_for('page.home'))

@bp.route("/logout", methods=("POST",))
@require_login
def logout():
    message = f'Logged out user: {get_current_user().name}'
    flash(message, 'success')

    set_logged_in_user_id(None)
    return redirect(url_for('page.home'))

@bp.route("/<id>")
def show(id):  # pylint: disable=redefined-builtin, invalid-name
    merchant = Merchant.find_by_id(id)
    builder = get_merchant_dao_builder()
    if not merchant:
        flash(f"Could not find user: {id}", "error")
        return redirect(url_for('merchant.index'))

    products = merchant.available_products()  # pylint: disable=redefined-outer-name
    merchant = builder.build(merchant)

    context = dict(
        merchant=merchant,
        products=products,
        can_edit=merchant.model == g.session_user,
        can_impersonate=merchant.can_impersonate()
        )
    return render_template('merchant/show.html', **context)

@bp.route("/dashboard")
@require_login
def dashboard():  # pylint: disable=redefined-builtin, invalid-name
    builder = get_merchant_dao_builder()
    merchant = builder.build(get_current_user())

    context = dict(merchant=merchant)
    return render_template('merchant/dashboard.html', **context)

@bp.route("/dashboard/products")
@require_login
def products():  # pylint: disable=redefined-builtin, invalid-name
    merchant = get_current_user()
    products = merchant.products  # pylint: disable=redefined-outer-name

    context = dict(products=products)
    return render_template('merchant/products.html', **context)

@bp.route("/dashboard/orders")
@require_login
def orders():  # pylint: disable=redefined-builtin, invalid-name
    merchant = get_current_user()
    total_revenue = merchant.total_revenue()
    # revenues_by_status = {
    #     status.value: merchant.revenue_by_status(status.value) for status in OrderStatus.all()
    #     }
    revenue_summary = merchant.revenue_summary()
    orders_summary = merchant.orders_summary()

    context = dict(
        products=products,
        total_revenue=total_revenue,
        # revenues_by_status=revenues_by_status,
        revenue_summary=revenue_summary,
        orders_summary=orders_summary,
        statuses=OrderStatus.all()
        )
    return render_template('merchant/orders.html', **context)

@bp.route("/update", methods=("GET", "POST"))
@require_login
def update():  # pylint: disable=redefined-builtin, invalid-name
    merchant = get_current_user()

    form = Form(obj=merchant)

    if form.validate_on_submit():
        merchant.update(**merchant_params(form))
        db.session.commit()

        return redirect(url_for('merchant.show', id=merchant.id))
    else:
        context = dict(
            merchant=merchant,
            form=form,
            form_action=url_for('merchant.update')
            )

        return render_template('merchant/update.html', **context)

def merchant_params(form):
    return dict(
        name=form.name.data
    )
