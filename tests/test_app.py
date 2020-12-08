import os

from betsy import create_app

def test_app_without_override():
    # test that repr gives a nice string
    os.environ['FLASK_ENV'] = 'TESTING'
    app = create_app()  # pylint: disable=redefined-outer-name
    assert app.config.get('TESTING')
