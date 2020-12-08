# pylint: disable=missing-module-docstring
import os

from flask import Flask
from flask_seeder import FlaskSeeder
from flask_bootstrap import Bootstrap

import betsy.storage.setup as db_setup
from betsy.storage.db import db
from betsy.auth.github import github
from betsy.helpers.session_context import register_session_context
from betsy.helpers.format_helper import register_format_helpers
from betsy.views import register_blueprints

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
        settings_obj = os.environ.get('FLASK_ENV', default='DEVELOPMENT')
        app.config.from_pyfile(f"{settings_obj.lower()}.py")
    else:
        # load the test config if passed in
        app.config.from_pyfile("config.py", silent=True)
        app.config.from_pyfile("testing.py")
        app.config.update(test_config)

    app.config.update(
        GITHUB_CLIENT_ID=os.environ.get('GITHUB_CLIENT_ID'),
        GITHUB_CLIENT_SECRET=os.environ.get('GITHUB_CLIENT_SECRET'),
        # SQLALCHEMY_ECHO=True,
        BOOTSTRAP_SERVE_LOCAL=True
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    Bootstrap(app)

    # register github oauth
    github.init_app(app)

    # register the database commands
    # breakpoint()
    db_setup.init_app(app, db)

    seeder = FlaskSeeder()
    seeder.init_app(app, db)

    register_blueprints(app)
    register_session_context(app)
    register_format_helpers(app)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="page.home")

    return app
