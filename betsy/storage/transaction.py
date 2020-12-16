import contextlib

@contextlib.contextmanager
def transaction(session, transaction_host):
    if transaction_host.transaction:
        raise RuntimeError("already in transaction")

    transaction_host.transaction = session
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        transaction_host.transaction = None
