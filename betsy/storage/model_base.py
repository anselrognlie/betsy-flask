from flask_sqlalchemy import Model

from sqlalchemy.schema import Column
from sqlalchemy.types import BigInteger, TIMESTAMP
from sqlalchemy.sql import functions as func

class ModelBase(Model):
    id = Column(BigInteger, primary_key=True)
    created_at = Column(TIMESTAMP(), nullable=False, server_default=func.now())  # pylint: disable=no-member

    @classmethod
    def find_by_id(cls, id):  # pylint: disable=invalid-name, redefined-builtin
        return cls.query.filter(cls.id == id).first()  # pylint: disable=no-member

    def update(self, **kwargs):
        for (key, value) in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
