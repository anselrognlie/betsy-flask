import contextlib

@contextlib.contextmanager
def transaction(session, transaction_host):
    transaction_host.transactions.append(session)

    try:
        yield session
        transaction_host.transactions.pop()
    except Exception:
        transaction_host.transactions.pop()
        if not transaction_host.transactions:
            session.rollback()
        raise

    if not transaction_host.transactions:
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise
