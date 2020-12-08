from flask import redirect
from flask import url_for

def redirect_home():
    return redirect(url_for('page.home'))
