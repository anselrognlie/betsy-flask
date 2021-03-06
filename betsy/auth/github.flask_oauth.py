from flask_oauth import OAuth

oauth = OAuth()

github = oauth.remote_app('github',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key='<your key here>',
    consumer_secret='<your secret here>'
)

@github.tokengetter
def get_github_token(token=None):
    return session.get('twitter_token')
