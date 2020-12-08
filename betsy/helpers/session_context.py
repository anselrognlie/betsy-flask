from flask import g

from ..dao import merchant as dao

def register_session_context(app):
    def session_context():
        return dict(
            session_user=dao.Merchant(g.session_user, g.allow_impersonation),
            logged_in=g.logged_in
            )

    app.context_processor(session_context)
