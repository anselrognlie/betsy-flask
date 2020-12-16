from flask import Blueprint
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for

from ..forms.category import Form
from ..models.category import Category
from ..logging.logger import logger
from .helper.auth_helper import require_login, is_logged_in

bp = Blueprint("category", __name__, url_prefix='/categories')

@bp.route("/")
def index():
    categories = Category.query.all()
    context = dict(
        categories=categories,
        can_edit=is_logged_in()
        )
    return render_template('category/index.html', **context)

@bp.route("/<id>")
def show(id):  # pylint: disable=redefined-builtin, invalid-name
    category = Category.find_by_id(id)
    if not category:
        flash(f"Could not find category: {id}", "error")
        return redirect(url_for('category.index'))

    products = category.available_products()

    context = dict(
        category=category,
        products=products,
        can_edit=is_logged_in()
        )
    return render_template('category/show.html', **context)

@bp.route("/create", methods=("GET", "POST"))
@require_login
def create():  # pylint: disable=redefined-builtin, invalid-name
    category = Category()
    return handle_shared_form(category, url_for('category.create'), 'category/create.html')

@bp.route("/<id>/update", methods=("GET", "POST"))
@require_login
def update(id):  # pylint: disable=redefined-builtin, invalid-name
    category = Category.find_by_id(id)
    return handle_shared_form(category, url_for('category.update', id=id), 'category/update.html')

def handle_shared_form(category, form_action, template):
    form = Form(obj=category)

    if form.validate_on_submit():
        try:
            category.update(**category_params(form))
            return redirect(url_for('category.show', id=category.id))

        except Exception:  # pylint: disable=broad-except
            msg = 'failed to save category'
            logger.exception(msg)
            flash(msg, 'error')

    context = dict(
        form=form,
        form_action=form_action
        )

    return render_template(template, **context)

def category_params(form):
    return dict(
        name=form.name.data
    )
