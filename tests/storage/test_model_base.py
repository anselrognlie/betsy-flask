from ..test_lib.helpers.model_helpers import (
    make_category
)

def test_update_ignores_invalid_fields(app, session):
    with app.app_context():
        category = make_category(session, 0)

        category.update(name='new name', invalid_field=True)

        assert category.name == 'new name'
        assert not hasattr(category, 'invalid_field')
