from flask import Blueprint
from flask import render_template

bp = Blueprint("page", __name__)

@bp.route("/")
def home():
    return render_template('page/home.html')
