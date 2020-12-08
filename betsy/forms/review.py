from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.core import SelectField

class Form(FlaskForm):
    rating = SelectField('Rating', choices=range(1, 5 + 1), coerce=int)
    comment = StringField('Comment')
