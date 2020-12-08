# from sqlalchemy import Column, Integer, Text, TIMESTAMP, FetchedValue, ForeignKey
from ..storage.db import db

# pylint: disable=line-too-long
product_category = db.Table('product_category',
    db.Column('product_id', db.Integer, db.ForeignKey("product.id"), nullable=False, primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey("category.id"), nullable=False, primary_key=True)
)
