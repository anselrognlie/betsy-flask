from betsy.models.order import Order

from .flask_helper import get_cart_id

class CartTestMixin:
    def get_cart(self):
        cart_id = get_cart_id(self.client)  # pylint: disable=no-member
        return Order.find_by_id(cart_id)

    def get_cart_items(self):
        cart = self.get_cart()
        return cart.order_items.all()
