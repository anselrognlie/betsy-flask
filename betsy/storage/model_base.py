from betsy.errors.model_error import ModelError
from flask_sqlalchemy import Model

from sqlalchemy.schema import Column
from sqlalchemy.types import BigInteger, TIMESTAMP
from sqlalchemy.sql import functions as func
from sqlalchemy import orm

from ..errors.validation_error import ValidationError
from .model_base_deps import model_base_deps
from .transaction import transaction

class ModelBase(Model):
    id = Column(BigInteger, primary_key=True)
    created_at = Column(TIMESTAMP(), nullable=False, server_default=func.now())  # pylint: disable=no-member

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.reconstruct()

    @orm.reconstructor
    def reconstruct(self):
        # pylint: disable=attribute-defined-outside-init
        self._validators = []
        self.init_errors()
        print(repr(self))

    def init_errors(self):
        # pylint: disable=attribute-defined-outside-init
        self.errors = []

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

    def reload(self):
        # pylint: disable=no-member
        self.db().session.refresh(self)

    def save(self):
        # require that we are in a transaction
        # this will ensure a rollback happens on error
        with ModelBase.transaction():
            # pylint: disable=no-member
            self.db().session.add(self)

    def destroy(self):
        # require that we are in a transaction
        # this will ensure a rollback happens on error
        with ModelBase.transaction():
            # pylint: disable=no-member
            self.db().session.delete(self)

    def add_validator(self, validator):
        self._validators.append(validator)

    def validate(self):
        self.init_errors()
        for validator in self._validators:
            try:
                validator(self)
            except ValidationError as ex:
                self.errors.append(ex)

        if self.errors:
            raise ModelError('validation failure')
