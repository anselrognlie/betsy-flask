from betsy.helpers import time as mytime

class MockNow:
    def __init__(self, now):
        self._old_mock = None
        self._now = now

    def enter(self):
        self._old_mock = mytime.TimeProvider.now
        mytime.TimeProvider.now = lambda: self._now

    def exit(self, _exc_type, _exc_value, _traceback):
        mytime.TimeProvider.now = self._old_mock
