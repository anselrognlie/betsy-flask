from wtforms.validators import ValidationError

class NotEmptyString:
    def __init__(self, message=None):
        self.message = message or 'field must not be empty'

    def __call__(self, form, field):
        stripped = str(field.data).strip()
        if len(stripped) == 0:
            raise ValidationError(self.message)
