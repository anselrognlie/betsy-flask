# pylint: disable=missing-module-docstring

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .model_base import ModelBase

db = SQLAlchemy(model_class=ModelBase)
migrate = Migrate()
