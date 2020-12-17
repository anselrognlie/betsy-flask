import pytest

from betsy.storage.transaction import transaction

from ..test_lib.mocks.mock_session import MockSession

class MockTransactionHost:
    def __init__(self):
        self.transactions = []

def test_commits_at_end():
    session = MockSession()
    host = MockTransactionHost()

    with transaction(session, host):
        pass

    assert session.commit_count == 1
    assert session.rollback_count == 0

def test_commits_once_for_nested_transactions():
    session = MockSession()
    host = MockTransactionHost()

    with transaction(session, host):
        with transaction(session, host):
            pass

    assert session.commit_count == 1
    assert session.rollback_count == 0

def test_rollback_on_error():
    session = MockSession()
    host = MockTransactionHost()

    with pytest.raises(RuntimeError) as error:
        with transaction(session, host):
            raise RuntimeError('transaction error')

    assert str(error.value) == 'transaction error'
    assert session.commit_count == 0
    assert session.rollback_count == 1

def test_rollback_called_once_on_error():
    session = MockSession()
    host = MockTransactionHost()

    with pytest.raises(RuntimeError) as error:
        with transaction(session, host):
            with transaction(session, host):
                raise RuntimeError('transaction error')

    assert str(error.value) == 'transaction error'
    assert session.commit_count == 0
    assert session.rollback_count == 1
