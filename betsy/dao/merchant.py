IMPERSONATION_PROVIDER = 'sample'

class Merchant:
    def __init__(self, merchant, allow_impersonation):
        self.model = merchant
        self._allow_impersonation = allow_impersonation

    @property
    def id(self):  # pylint: disable=invalid-name
        return self.model.id if self.model else None

    @property
    def name(self):
        return self.model.name if self.model else None

    @property
    def email(self):
        return self.model.email if self.model else None

    @property
    def provider(self):
        return self.model.provider if self.model else None

    @property
    def uid(self):
        return self.model.uid if self.model else None

    @property
    def products(self):
        return self.model.products if self.model else []

    @property
    def created_at(self):
        return self.model.created_at if self.model else None

    @property
    def name_safe(self):
        return self.name or f"id: {self.id}"

    def can_impersonate(self):
        return self._allow_impersonation and self.provider == IMPERSONATION_PROVIDER
