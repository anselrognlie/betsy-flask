from betsy.dao.merchant import Merchant as wrap

from ..test_lib.helpers.model_helpers import (
    make_merchant
)

def test_dao_properties(app, session):
    with app.app_context():
        merchant = make_merchant(session, 0)
        dao = wrap(merchant, True)

        assert dao.id == merchant.id
        assert dao.name == merchant.name
        assert dao.email == merchant.email
        assert dao.provider == merchant.provider
        assert dao.uid == merchant.uid
        assert len(dao.products.all()) == len(merchant.products.all())
        assert dao.created_at == merchant.created_at
        assert dao.name_safe == merchant.name
        assert dao.can_impersonate()

def test_empty_dao_properties():
    dao = wrap(None, True)

    assert not dao.id
    assert not dao.name
    assert not dao.email
    assert not dao.provider
    assert not dao.uid
    assert len(dao.products) == 0
    assert not dao.created_at
    assert dao.name_safe == 'id: None'
    assert not dao.can_impersonate()

def test_no_impersonation(app, session):
    with app.app_context():
        merchant = make_merchant(session, 0)
        dao = wrap(merchant, False)

        assert not dao.can_impersonate()
