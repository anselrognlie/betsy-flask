from ...errors.validation_error import ValidationError

class RequiredValidator:
    def __init__(self, field, trim=True, message = 'is required'):
        self.field = field
        self.trim = trim
        self.message = message

    def __call__(self, instance):
        value = getattr(instance, self.field)

        if self.trim:
            value = str(value).strip()

        if not value:
            raise ValidationError(self, self.field, self.message)
