from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.core import BooleanField, IntegerField
from wtforms.validators import InputRequired

from .validators.not_empty_string import NotEmptyString
from .fields.dollar_field import DollarField

class Form(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), NotEmptyString()])
    photo_url = StringField('Photo URL')
    description = StringField('Description', validators=[InputRequired(), NotEmptyString()])
    price = DollarField('Price', validators=[InputRequired()])
    stock = IntegerField('Stock', validators=[InputRequired()])
    discontinued = BooleanField('Discontinued')
