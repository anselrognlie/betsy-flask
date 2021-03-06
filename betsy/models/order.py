from sqlalchemy.ext.associationproxy import association_proxy

from .validations.required_if_validator import RequiredIfValidator
from .validations.required_validator import RequiredValidator
from .validations.email_validator import EmailValidator
from ..errors.model_error import ModelError
from ..helpers import time as mytime
from ..storage.db import db
from ..storage.model_base import ModelBase
from .order_item import OrderItem
from .order_status import OrderStatus
from .product import Product

class Order(ModelBase):
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

    def register_validators(self):
        self.add_validator(RequiredIfValidator('email', Order.paid_or_completed))
        self.add_validator(RequiredIfValidator('mailing_address', Order.paid_or_completed))
        self.add_validator(RequiredIfValidator('cc_name', Order.paid_or_completed))
        self.add_validator(RequiredIfValidator('cc_number', Order.paid_or_completed))
        self.add_validator(RequiredIfValidator('cc_exp', Order.paid_or_completed))
        self.add_validator(RequiredIfValidator('cc_cvv', Order.paid_or_completed))
        self.add_validator(RequiredIfValidator('cc_zipcode', Order.paid_or_completed))
        self.add_validator(RequiredIfValidator('ordered_date', Order.paid_or_completed))
        self.add_validator(RequiredValidator('status'))
        self.add_validator(EmailValidator('email', allow_empty=True))

    @staticmethod
    def paid_or_completed(instance):
        return instance.status in (OrderStatus.PAID.value, OrderStatus.COMPLETED.value)

    def __repr__(self):
        return f"<Order email='{self.email}'>"

    @staticmethod
    def make_cart():
        cart = Order(status=OrderStatus.PENDING.value)
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
            return existing_item
        else:
            with Order.transaction():
                item = OrderItem(order=self, product=product, quantity=quantity)
                item.save()
                self.save()
            return item

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
