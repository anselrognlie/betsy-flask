from .required_validator import RequiredValidator

class RequiredIfValidator:
    def __init__(self, field, check, trim=True, message = 'is required'):
        self.check = check
        self.required = RequiredValidator(field, trim, message)

    def __call__(self, instance):
        if self.check(instance):
            self.required(instance)
