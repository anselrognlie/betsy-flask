from functools import wraps

from flask_github import GitHubError

from .github import github

class GithubAuth:
    # pylint: disable=invalid-name
    def auth_hash_sink(self, f):
        @wraps(f)
        def decorated(oauth_token, *args, **kwargs):
            auth_hash = self.get_auth_hash(oauth_token)
            return f(*((auth_hash,) + args), **kwargs)
        return decorated

    def get_auth_hash(self, oauth_token):
        if oauth_token is None: return None  # pylint: disable=multiple-statements

        try:
            result = github.get('/user', access_token=oauth_token)
            auth_hash = dict(
                uid=result.get('id'),
                email=result.get('email'),
                name=result.get('name') or result.get('login'),
                provider='github'
            )

            if auth_hash['email'] is None:
                result = github.get('/user/emails', access_token=oauth_token)
                auth_hash['email'] = result[0]['email']

            return auth_hash

        except GitHubError:
            return None
