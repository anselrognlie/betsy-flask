from flask_github import GitHubError

from betsy.auth.github_auth import github_auth

from ..test_lib.mocks.simple_mocker import SimpleMocker
from ..test_lib.mocks.mock_github_get import MockGithubGet

def test_github_auth_no_token():
    result = github_auth.get_auth_hash(None)
    assert result is None

def test_github_auth_get_token():
    mock = MockGithubGet()
    mock.add_response('/user', 'oauth_token', lambda *args: dict(
        id='1234',
        email=None,
        name='user'
    ))
    mock.add_response('/user/emails', 'oauth_token', lambda *args: [dict(email='user@email.com')])

    expected = dict(
        uid='1234',
        email='user@email.com',
        name='user',
        provider='github'
    )

    with SimpleMocker([mock]):
        result = github_auth.get_auth_hash('oauth_token')
        assert result == expected

def test_github_auth_no_secondary_call():
    mock = MockGithubGet()
    mock.add_response('/user', 'oauth_token', lambda *args: dict(
        id='1234',
        email='user@email.com',
        name='user'
    ))

    expected = dict(
        uid='1234',
        email='user@email.com',
        name='user',
        provider='github'
    )

    with SimpleMocker([mock]):
        result = github_auth.get_auth_hash('oauth_token')
        assert result == expected

def test_github_with_error():
    def raise_error(*_args):
        raise GitHubError('invalid operation')

    mock = MockGithubGet()
    mock.add_response('/user', 'oauth_token', raise_error)

    with SimpleMocker([mock]):
        result = github_auth.get_auth_hash('oauth_token')
        assert not result
