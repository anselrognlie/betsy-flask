from sqlalchemy.ext.associationproxy import association_proxy

from .order_item import OrderItem
from .order_status import OrderStatus
from .product import Product
from ..errors.model_error import ModelError
from ..helpers import time as mytime
from ..storage.db import db

class Order(db.Model):
    # pylint: disable=missing-class-docstring, too-few-public-methods
    __tablename__ = 'order'

    email = db.Column(db.String())
    mailing_address = db.Column(db.String())
    cc_name = db.Column(db.String())
    cc_number = db.Column(db.String())
    cc_exp = db.Column(db.String())
    cc_cvv = db.Column(db.String())
    cc_zipcode = db.Column(db.String())
    status = db.Column(db.String(), nullable=False, default='pending')
    ordered_date = db.Column(db.TIMESTAMP())
    order_items = db.relationship("OrderItem", lazy='dynamic')
    products = association_proxy('order_items', 'product')

    def __repr__(self):
        return f"<Order email='{self.email}'>"

    @staticmethod
    def make_cart():
        cart = Order()
        cart.save()

        return cart

    def total(self):
        return sum(
            item.subtotal() for item in self.order_items  # pylint: disable=not-an-iterable
        )

    def find_item_by_product(self, product):
        return self.order_items.filter(OrderItem.product_id == product.id).first()  # pylint: disable=no-member

    def add_product(self, product, quantity):
        # if there is an existing order_item, update the desired quantity
        existing_item = self.find_item_by_product(product)
        if existing_item:
            quantity += existing_item.quantity

        if quantity > product.stock:
            raise ModelError('invalid stock for order')

        if existing_item:
            existing_item.update_quantity(quantity)
        else:
            with Order.transaction():
                self.order_items.append(OrderItem(product=product, quantity=quantity))  # pylint: disable=no-member
                self.save()

    def update_product(self, product, quantity):
        # if there is an existing order_item, update the desired quantity
        existing_item = self.find_item_by_product(product)
        if existing_item is None:
            raise ModelError('invalid product')

        existing_item.update_quantity(quantity)

    def can_checkout(self):
        if self.status != OrderStatus.PENDING.value:
            return False

        if self.order_items.count() == 0:  # pylint: disable=no-member
            return False

        for item in self.order_items:  # pylint: disable=not-an-iterable
            if not item.is_valid():
                return False

        return True

    def checkout(self, **kwargs):
        if not self.can_checkout():
            raise ModelError('unable to checkout')

        with Order.transaction():
            self.update(**kwargs)
            self.status = OrderStatus.PAID.value
            self.ordered_date = mytime.TimeProvider.now()

            for item in self.order_items:  # pylint: disable=not-an-iterable
                item.prepare_checkout()

            self.save()

    def can_cancel(self):
        if self.status != OrderStatus.PAID.value:
            return False

        for item in self.order_items:  # pylint: disable=not-an-iterable
            if item.is_shipped():
                return False

        return True

    def cancel(self):
        if not self.can_cancel():
            raise ModelError("order cannot be cancelled")

        with Order.transaction():
            self.status = OrderStatus.CANCELLED.value
            for item in self.order_items:  # pylint: disable=not-an-iterable
                item.prepare_cancel()
            self.save()

    def items_for_merchant(self, merchant):
        # pylint: disable=no-member
        return self.order_items.join(OrderItem.product).filter(Product.merchant_id == merchant.id)

    def refresh_status(self):

        if self.status == OrderStatus.PAID.value:
            complete = True
            for item in self.order_items:  # pylint: disable=not-an-iterable
                if not item.shipped_date:
                    complete = False
                    break

            if complete:
                with Order.transaction():
                    self.status = OrderStatus.COMPLETED.value
                    self.save()
