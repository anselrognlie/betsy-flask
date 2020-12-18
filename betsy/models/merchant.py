from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from betsy.models.order_status import OrderStatus

from ..storage.db import db
from ..storage.model_base import ModelBase
from .product import Product
from .order_item import OrderItem
from .order import Order
from .record import Record

class Merchant(ModelBase):
    # pylint: disable=missing-class-docstring, too-few-public-methods
    __tablename__ = 'merchant'
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    provider = db.Column(db.String(), nullable=False)
    uid = db.Column(db.String(), nullable=False)
    products = db.relationship("Product", lazy="dynamic")

    def __repr__(self):
        return f"<Merchant name='{self.name}'>"

    @staticmethod
    def find_by_provider_uid(provider, uid):
        return Merchant.query.filter(
            Merchant.provider == str(provider), Merchant.uid == str(uid)
            ).first()

    def available_products(self):
        # pylint: disable=singleton-comparison, no-member
        return self.products.filter(Product.discontinued == False, Product.stock > 0)

    def total_revenue(self):
        items = (
            OrderItem.find_by_merchant(self).
                join(OrderItem.order).
                filter(or_(Order.status == 'paid', Order.status == 'completed'))
        )

        return sum(item.subtotal() for item in items)

    def revenue_by_status(self, status):
        items = (
            OrderItem.find_by_merchant(self).
                join(OrderItem.order).
                filter(Order.status == status)
        )

        return sum(item.subtotal() for item in items)

    def revenue_summary(self):
        items = (
            OrderItem.find_by_merchant(self).
                join(OrderItem.order)
        )

        summary = {}
        for item in items:
            status = item.order.status
            subtotals = summary.get(status)
            if not subtotals:
                subtotals = []
                summary[status] = subtotals

            subtotals.append(item.subtotal())

        for status in OrderStatus.all():
            subtotals = summary.get(status, [])
            status_summary = Record()
            status_summary.count = len(subtotals)
            status_summary.total = sum(subtotals)

            summary[status] = status_summary

        return summary

    def orders_summary(self):
        items = (
            OrderItem.find_by_merchant(self).
                join(OrderItem.order)
        )

        summary = {}
        for item in items:
            status = item.order.status
            orders = summary.get(status)
            if not orders:
                orders = {}
                summary[status] = orders

            order = orders.get(item.order.id)
            if not order:
                order = Record()
                order.order = item.order
                order.items = []
                orders[item.order.id] = order

            order.items.append(item)

        return summary

    @staticmethod
    def make_from_auth_hash(auth_hash):
        if not auth_hash:
            return None

        user = Merchant.find_by_provider_uid('github', auth_hash['uid'])
        if user is None:
            user = Merchant._make_user_internal(auth_hash)

        return user

    @staticmethod
    def _make_user_internal(auth_hash):
        try:
            user = Merchant(**auth_hash)
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            return None
