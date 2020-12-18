class MockFlash():
    def __init__(self):
        self.flashes = []

    def flash(self, message, category='missing'):
        self.flashes.append(dict(message=message, category=category))
