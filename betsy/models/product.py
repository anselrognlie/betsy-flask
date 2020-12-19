from sqlalchemy.ext.associationproxy import association_proxy

from .validations.required_validator import RequiredValidator
from .validations.range_validator import RangeValidator
from ..storage.db import db
from ..storage.model_base import ModelBase
from .product_category import product_category

class Product(ModelBase):
    # pylint: disable=missing-class-docstring, too-few-public-methods
    __tablename__ = 'product'
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String())
    price = db.Column(db.Integer, nullable=False)
    photo_url = db.Column(db.String())
    stock = db.Column(db.Integer, nullable=False)
    discontinued = db.Column(db.Boolean, nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey("merchant.id"), nullable=False)
    merchant = db.relationship("Merchant", back_populates="products")
    categories = db.relationship(
        'Category', secondary=product_category, back_populates='products', lazy='dynamic'
        )
    reviews = db.relationship("Review", lazy='dynamic')
    order_items = db.relationship("OrderItem", lazy='dynamic')
    orders = association_proxy('order_items', 'order')

    def register_validators(self):
        self.add_validator(RequiredValidator('name'))
        self.add_validator(RequiredValidator('description'))
        self.add_validator(RequiredValidator('price'))
        self.add_validator(RangeValidator('price', min_val=1))
        self.add_validator(RequiredValidator('stock'))
        self.add_validator(RangeValidator('stock', min_val=0))
        self.add_validator(RequiredValidator('discontinued'))

    def __repr__(self):
        return f"<Product name='{self.name}'>"

    def update_categories(self, categories):
        self.categories = categories
        self.save()

    def is_available(self):
        return self.stock > 0 and not self.discontinued

    def can_review(self, user):
        if self.discontinued:
            return False

        return user is None or user.id != self.merchant_id

    def can_edit(self, user):
        return user is not None and user.id == self.merchant_id

    @staticmethod
    def available_products():
        # pylint: disable=singleton-comparison
        return Product.query.filter(Product.discontinued == False, Product.stock > 0)
