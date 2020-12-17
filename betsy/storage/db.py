# pylint: disable=missing-module-docstring

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import event

from .model_base import ModelBase
from .model_base_deps import model_base_deps

db = SQLAlchemy(model_class=ModelBase)
migrate = Migrate()

model_base_deps.db = db

@event.listens_for(db.session, 'before_flush')
def perform_validation_before_flush(session, _flush_context, _instances):
    # validate new and dirty items
    object_list = []
    object_list.extend(session.new)
    object_list.extend(session.dirty)

    for model in object_list:
        if isinstance(model, ModelBase):
            model.validate()
