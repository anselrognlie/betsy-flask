from betsy.errors.validation_error import ValidationError
from ..helpers import time as mytime
from ..storage.db import db
from ..storage.model_base import ModelBase
from ..errors.model_error import ModelError
from .product import Product
from .order_status import OrderStatus
from .validations.range_validator import RangeValidator

class OrderItem(ModelBase):
    # pylint: disable=missing-class-docstring, too-few-public-methods
    __tablename__ = 'order_item'
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    product = db.relationship("Product", back_populates="order_items")
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    order = db.relationship("Order", back_populates="order_items")
    quantity = db.Column(db.Integer, nullable=False)
    shipped_date = db.Column(db.TIMESTAMP())
    purchase_price = db.Column(db.Integer)

    def register_validators(self):
        self.add_validator(RangeValidator('quantity', min_val=1))
        self.add_validator(self.order_status_validation)

    def order_status_validation(self, _instance):
        # paid orders must have a purchase_price
        if (
            self.shipped_date is not None or
            self.order.status == OrderStatus.PAID.value # pylint: disable=no-member
        ):
            if self.purchase_price is None:
                raise ValidationError(self, 'purchase_price', 'must be set')

    def __repr__(self):
        return f"<OrderItem product_id='{self.product_id}' order_id='{self.order_id}'>"

    def product_name(self):
        return self.product.name  # pylint: disable=no-member

    def product_price(self):
        # pylint: disable=no-member
        return self.purchase_price or self.product.price

    def is_product_available(self):
        # pylint: disable=no-member
        return self.product.is_available()

    def subtotal(self):
        return self.product_price() * self.quantity

    def delete(self):
        # only destroy if in a pending order
        if self.order.status != OrderStatus.PENDING.value:  # pylint: disable=no-member
            raise ModelError("order item cannot be deleted")

        self.destroy()

    def is_valid(self):
        return self.quantity <= self.product.stock  # pylint: disable=no-member

    def prepare_checkout(self):
        # pylint: disable=no-member
        self.purchase_price = self.product.price
        self.product.stock -= self.quantity
        self.save()

    def is_shipped(self):
        return self.shipped_date is not None

    def prepare_cancel(self):
        # pylint: disable=no-member
        self.product.stock += self.quantity
        self.save()

    def can_ship(self):
        return self.shipped_date is None and self.order.status == OrderStatus.PAID.value  # pylint: disable=no-member

    def ship(self, merchant):
        if not self.can_ship():
            raise ModelError("order item cannot be shipped")

        if not merchant or merchant.id != self.product.merchant_id:  # pylint: disable=no-member
            raise ModelError("order item cannot be shipped")

        with OrderItem.transaction():
            self.shipped_date = mytime.TimeProvider.now()
            self.save()
            self.order.refresh_status()  # pylint: disable=no-member

    def update_quantity(self, quantity):
        if quantity < 0 or quantity > self.product.stock:  # pylint: disable=no-member
            raise ModelError('invalid product quantity')

        if quantity == 0:
            self.delete()
            return

        with OrderItem.transaction():
            self.quantity = quantity
            self.save()

    @staticmethod
    def find_by_merchant(merchant):
        return (
            OrderItem.query.
                join(OrderItem.product).
                filter(Product.merchant_id == merchant.id)
        )
