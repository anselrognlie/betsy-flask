from ..merchant import Merchant as dao  # pylint: disable=relative-beyond-top-level

class MerchantDaoBuilder:
    def __init__(self, allow_impersonation=False):
        self.allow_impersonation = allow_impersonation

    def build(self, merchant):
        return dao(merchant, self.allow_impersonation)
