from ..errors.validation_error import ValidationError

class UniqueValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, instance):
        results = type(instance).query.filter(
            getattr(type(instance), self.field) == getattr(instance, self.field)
        ).all()

        if len(results) >= 1:
            result = results[0]
            if result.id != instance.id:
                raise ValidationError(self, 'name', 'must be unique')
