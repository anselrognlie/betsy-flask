class ValidationError(Exception):
    def __init__(self, instance, field, message, *args):
        super().__init__(*args)
        self.instance = instance
        self.field = field
        self.message = message
