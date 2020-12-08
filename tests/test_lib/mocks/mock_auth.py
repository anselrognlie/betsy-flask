from flask import redirect, url_for

from betsy.auth.github_auth import github_auth
from betsy.auth.github import github

class MockAuth:
    def __init__(self, auth_hash, authorized=True):
        self.authorized = authorized
        self._auth_hash = auth_hash
        self._old_make_auth_hash = None
        self._old_get_auth_hash = None
        self._old_authorize = None

    def get_auth_hash(self, _oauth_token):
        return self._auth_hash if self.authorized else None

    def authorize(self, *_args, **_kwargs):
        return redirect(url_for('auth.authorized'))

    def enter(self):
        self._old_get_auth_hash = github_auth.get_auth_hash
        self._old_authorize = github.authorize
        github_auth.get_auth_hash = self.get_auth_hash
        github.authorize = self.authorize

    def exit(self, _exc_type, _exc_value, _traceback):
        github_auth.get_auth_hash = self._old_get_auth_hash
        github.authorize = self._old_authorize
