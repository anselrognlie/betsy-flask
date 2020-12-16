from betsy.wsgi import app

def test_load_wsgi():
    assert not app is None
