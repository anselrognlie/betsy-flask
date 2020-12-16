from flask_sqlalchemy import Model

from sqlalchemy.schema import Column
from sqlalchemy.types import BigInteger, TIMESTAMP
from sqlalchemy.sql import functions as func

from .model_base_deps import model_base_deps
from .transaction import transaction

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
        self.save()

    @classmethod
    def db(cls):  # pylint: disable=invalid-name
        return model_base_deps.db

    @classmethod
    def transaction(cls):
        return transaction(cls.db().session, model_base_deps)

    def save(self):
        # pylint: disable=no-member
        self.db().session.add(self)

        if not model_base_deps.transaction:
            self.db().session.commit()
