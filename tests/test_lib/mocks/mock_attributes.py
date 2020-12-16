class MockAttributes:
    def __init__(self):
        self._replacements = []
        self._originals = []

    def register(self, cls, method, mock):
        self._replacements.append((cls, method, mock))

    def enter(self):
        for cls, method, mock in self._replacements:
            old_method = getattr(cls, method)
            self._originals.append((cls, method, old_method))
            setattr(cls, method, mock)

    def exit(self, _exc_type, _exc_value, _traceback):
        for cls, method, old_method in self._originals:
            setattr(cls, method, old_method)
