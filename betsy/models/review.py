from ..storage.db import db
from ..storage.model_base import ModelBase
from .validations.range_validator import RangeValidator

class Review(ModelBase):
    # pylint: disable=missing-class-docstring, too-few-public-methods
    __tablename__ = 'review'
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String())
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    product = db.relationship("Product", back_populates="reviews")

    def __repr__(self):
        return f"<Review rating='{self.rating}'>"

    def register_validators(self):
        self.add_validator(RangeValidator('rating', 1, 5))
