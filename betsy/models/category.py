from betsy.storage.model_base import ModelBase
from betsy.errors.validation_error import ValidationError
from ..storage.db import db
from ..storage.model_base import ModelBase
from .product_category import product_category
from .product import Product

class Category(ModelBase):
    # pylint: disable=missing-class-docstring, too-few-public-methods
    __tablename__ = 'category'
    name = db.Column(db.String(), nullable=False)
    products = db.relationship(
        'Product', secondary=product_category, back_populates='categories', lazy='dynamic'
        )

    def register_validators(self):
        self.add_validator(self.require_unique_name)

    def __repr__(self):
        return f"<Category name='{self.name}'>"

    def available_products(self):
        # pylint: disable=singleton-comparison, no-member
        return self.products.filter(Product.discontinued == False, Product.stock > 0)

    def require_unique_name(self):
        error = False
        for _ in range(1):
            results = Category.query.filter(Category.name == self.name).all()
            if len(results) > 1:
                error = True
                break

            if len(results) == 1:
                if not self.id:
                    error = True
                    break

                result = results[0]
                if result.id != self.id:
                    error = True
                    break

        if error:
            raise ValidationError(self, 'name', 'must be unique')
