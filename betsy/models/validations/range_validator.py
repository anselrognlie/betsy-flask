from ...errors.validation_error import ValidationError

class RangeValidator:
    def __init__(self, field, min_val, max_val, message = None):
        self.field = field
        self.min_val = min_val
        self.max_val = max_val
        self.message = message or f'must be between {min_val} and {max_val}'

    def __call__(self, instance):
        error = True
        value = getattr(instance, self.field)

        try:
            value = int(value)
            if self.min_val <= value <= self.max_val:
                error = False
        except TypeError:
            pass

        if error:
            raise ValidationError(self, self.field, self.message)
