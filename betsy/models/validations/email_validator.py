import re

from ...errors.validation_error import ValidationError

class EmailValidator:
    def __init__(self, field, trim=True, message = 'must be a valid email'):
        self.field = field
        self.trim = trim
        self.message = message

    def __call__(self, instance):
        value = getattr(instance, self.field)

        if self.trim:
            value = str(value).strip()

        # uses a simple regex strategy from
        # https://stackoverflow.com/questions/8022530/how-to-check-for-valid-email-address

        regex = r'[^@]+@[^@]+\.[^@]+'
        if not re.search(regex, value):
            raise ValidationError(self, self.field, self.message)
