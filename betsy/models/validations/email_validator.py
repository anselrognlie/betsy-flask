import re

from ...errors.validation_error import ValidationError

class EmailValidator:
    def __init__(self, field, allow_empty=False, trim=True, message='must be a valid email'):
        self.field = field
        self.trim = trim
        self.message = message
        self.allow_empty = allow_empty

    def __call__(self, instance):
        value = getattr(instance, self.field)

        if self.trim:
            value = str(value).strip()

        if not value and self.allow_empty:
            return

        # uses a simple regex strategy from
        # https://stackoverflow.com/questions/8022530/how-to-check-for-valid-email-address

        regex = r'[^@]+@[^@]+\.[^@]+'
        if not re.search(regex, value):
            raise ValidationError(self, self.field, self.message)
