# pylint: disable=missing-module-docstring

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .model_base_deps import model_base_deps

db = SQLAlchemy()
migrate = Migrate()

model_base_deps.db = db
