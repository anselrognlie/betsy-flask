from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired

from .validators.not_empty_string import NotEmptyString

class Form(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), NotEmptyString()])
    mailing_address = StringField('Mailing Address', validators=[InputRequired(), NotEmptyString()])
    cc_name = StringField('Name on Credit Card', validators=[InputRequired(), NotEmptyString()])
    cc_number = StringField('Credit Card#', validators=[InputRequired(), NotEmptyString()])
    cc_exp = StringField('Expiration Date', validators=[InputRequired(), NotEmptyString()])
    cc_cvv = StringField('CVV', validators=[InputRequired(), NotEmptyString()])
    cc_zipcode = StringField('Zipcode', validators=[InputRequired(), NotEmptyString()])
