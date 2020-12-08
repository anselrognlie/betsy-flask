from betsy.models.order import Order

class MockCheckout:
    def __init__(self, checkout_result):
        self._old_checkout = None
        self._checkout_result = checkout_result

    def checkout(self, **_kwargs):
        return self._checkout_result

    def enter(self):
        result = self._checkout_result
        self._old_checkout = Order.checkout
        Order.checkout = lambda self, **_kwargs: result

    def exit(self, _exc_type, _exc_value, _traceback):
        Order.checkout = self._old_checkout
