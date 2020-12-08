import betsy.views.helper.order_helper as order_helper

class MockCart:
    def __init__(self, cart):
        self._old_get_cart = None
        self._cart = cart

    def enter(self):
        self._old_get_cart = order_helper.get_cart
        order_helper.get_cart = lambda: self._cart

    def exit(self, _exc_type, _exc_value, _traceback):
        order_helper.get_cart = self._old_get_cart
