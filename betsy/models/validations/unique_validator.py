from ...errors.validation_error import ValidationError

class UniqueValidator:
    def __init__(self, field, message = 'must be unique', trim = True):
        self.field = field
        self.message = message
        self.trim = trim

    def __call__(self, instance):
        value = getattr(instance, self.field)
        if self.trim:
            value = str(value).strip()

        results = type(instance).query.filter(
            getattr(type(instance), self.field) == value
        ).all()

        if len(results) >= 1:
            result = results[0]
            if result.id != instance.id:
                raise ValidationError(self, self.field, self.message)
