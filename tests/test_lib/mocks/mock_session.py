class MockSession:
    def __init__(self):
        self.commit_called = False
        self.rollback_called = False

    def commit(self):
        self.commit_called = True

    def rollback(self):
        self.rollback_called = True
