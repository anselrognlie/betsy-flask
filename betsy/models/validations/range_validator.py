from ...errors.validation_error import ValidationError

class RangeValidator:
    def __init__(self, field, min_val = None, max_val = None, message = None):
        self.field = field

        if (min_val is None and max_val is None):
            raise ValueError('must supply at least one of min_val or max_val')

        self.min_val = min_val
        self.max_val = max_val
        self.message = message or self.make_error_message()

    def make_error_message(self):
        if self.min_val is not None:
            if self.max_val is not None:
                return f'must be between {self.min_val} and {self.max_val}'
            else:
                return f'must be at least {self.min_val}'
        else:
            return f'must be at most {self.max_val}'

    def __call__(self, instance):
        error = True
        value = getattr(instance, self.field)

        try:
            value = int(value)
            if self.min_val is not None:
                if self.max_val is not None:
                    if self.min_val <= value <= self.max_val:
                        error = False
                else:
                    if self.min_val <= value:
                        error = False
            else:
                if value <= self.max_val:
                    error = False
        except TypeError:
            pass

        if error:
            raise ValidationError(self, self.field, self.message)
