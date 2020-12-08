from flask_wtf import FlaskForm
from wtforms_sqlalchemy.orm import QuerySelectMultipleField

from ..models.category import Category

def fill_categories():
    return Category.query

class Form(FlaskForm):
    categories = QuerySelectMultipleField('Categories', query_factory=fill_categories,
        get_label='name')
