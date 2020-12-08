from betsy.auth.github import github

class MockGithubGet:
    def __init__(self):
        self._old_get = None
        self._requests = []

    def enter(self):
        self._old_get = github.get
        github.get = lambda path, access_token=None: self.get(path, access_token)

    def exit(self, _exc_type, _exc_value, _traceback):
        github.get = self._old_get

    def get(self, path, access_token):
        for request_path, request_token, handler in self._requests:
            if request_path == path and request_token == access_token:
                return handler(path, access_token)

        return None

    def add_response(self, path, access_token, handler):
        self._requests.append((path, access_token, handler))
