from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired

from .validators.not_empty_string import NotEmptyString

class Form(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), NotEmptyString()])
