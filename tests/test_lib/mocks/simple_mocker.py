class SimpleMocker:
    def __init__(self, mockers):
        self._mockers = mockers

    def __enter__(self):
        for mocker in self._mockers:
            mocker.enter()

    def __exit__(self, exc_type, exc_value, traceback):
        for mocker in self._mockers:
            mocker.exit(exc_type, exc_value, traceback)
