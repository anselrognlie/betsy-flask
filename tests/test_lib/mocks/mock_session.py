class MockSession:
    def __init__(self):
        self.commit_called = False
        self.rollback_called = False
        self.commit_count = 0
        self.rollback_count = 0

    def commit(self):
        self.commit_count += 1
        self.commit_called = True

    def rollback(self):
        self.rollback_count += 1
        self.rollback_called = True
