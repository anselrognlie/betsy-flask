from ..storage.db import db
from ..storage.model_base import ModelBase

from .product_category import product_category
from .product import Product

from .validations.unique_validator import UniqueValidator
from .validations.required_validator import RequiredValidator

class Category(ModelBase):
    # pylint: disable=missing-class-docstring, too-few-public-methods
    __tablename__ = 'category'
    name = db.Column(db.String(), nullable=False)
    products = db.relationship(
        'Product', secondary=product_category, back_populates='categories', lazy='dynamic'
        )

    def register_validators(self):
        self.add_validator(UniqueValidator('name'))
        self.add_validator(RequiredValidator('name'))

    def __repr__(self):
        return f"<Category name='{self.name}'>"

    def available_products(self):
        # pylint: disable=singleton-comparison, no-member
        return self.products.filter(Product.discontinued == False, Product.stock > 0)
