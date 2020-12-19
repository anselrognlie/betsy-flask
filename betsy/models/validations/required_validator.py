from ...errors.validation_error import ValidationError

class RequiredValidator:
    def __init__(self, field, trim=True, message = 'is required'):
        self.field = field
        self.trim = trim
        self.message = message

    def __call__(self, instance):
        value = None
        str_value = None

        if hasattr(instance, self.field):
            value = getattr(instance, self.field)
            str_value = str(value) if value is not None else None

            if str_value and self.trim:
                str_value = str_value.strip()

        if value is None or not str_value:
            raise ValidationError(self, self.field, self.message)
