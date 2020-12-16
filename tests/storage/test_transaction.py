import pytest

from betsy.storage.transaction import transaction

class MockTransactionHost:
    def __init__(self):
        self.transaction = None

class MockSession:
    def __init__(self):
        self.commit_called = False
        self.rollback_called = False

    def commit(self):
        self.commit_called = True

    def rollback(self):
        self.rollback_called = True

def test_prevent_nested_transaction():
    session = MockSession()
    host = MockTransactionHost()
    host.transaction = session

    with pytest.raises(RuntimeError):
        with transaction(session, host):
            pass

    assert not session.commit_called
    assert not session.rollback_called

def test_commits_at_end():
    session = MockSession()
    host = MockTransactionHost()

    with transaction(session, host):
        pass

    assert session.commit_called
    assert not session.rollback_called

def test_rollback_on_error():
    session = MockSession()
    host = MockTransactionHost()

    with pytest.raises(RuntimeError) as error:
        with transaction(session, host):
            raise RuntimeError('transaction error')

    assert str(error.value) == 'transaction error'
    assert not session.commit_called
    assert session.rollback_called
