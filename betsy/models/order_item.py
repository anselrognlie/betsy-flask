from ..storage.db import db
from .product import Product
from .order_status import OrderStatus
from ..helpers import time as mytime

class OrderItem(db.Model):
    # pylint: disable=missing-class-docstring, too-few-public-methods
    __tablename__ = 'order_item'
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    product = db.relationship("Product", back_populates="order_items")
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    order = db.relationship("Order", back_populates="order_items")
    quantity = db.Column(db.Integer, nullable=False)
    shipped_date = db.Column(db.TIMESTAMP())
    purchase_price = db.Column(db.Integer)

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

    def destroy(self):
        # only destroy if in a pending order
        if self.order.status != OrderStatus.PENDING.value:  # pylint: disable=no-member
            return False

        db.session.delete(self)
        db.session.commit()
        return True

    def is_valid(self):
        return self.quantity <= self.product.stock  # pylint: disable=no-member

    def prepare_commit(self):
        # pylint: disable=no-member
        self.purchase_price = self.product.price
        self.product.stock -= self.quantity

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
            return False

        if not merchant or merchant.id != self.product.merchant_id:  # pylint: disable=no-member
            return False

        self.shipped_date = mytime.TimeProvider.now()
        return self.order.refresh_status()  # pylint: disable=no-member

    @staticmethod
    def find_by_merchant(merchant):
        return (
            OrderItem.query.
                join(OrderItem.product).
                filter(Product.merchant_id == merchant.id)
        )
