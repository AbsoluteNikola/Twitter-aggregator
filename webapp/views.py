from webapp import app, login
from aggregator import Twit, User
from functools import wraps
from pprint import pprint
from flask import session, request, url_for, render_template, abort, redirect


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template("index.html.j2")


def login_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        logged_in = session.pop('logged_in', False)
        if logged_in:
            session['logged_in'] = True
            return func(*args, **kwargs)
        else:
            session['logged_in'] = False
            session['next'] = request.url
            return redirect(url_for('login'))
    return deco  


@app.route('/user')
@login_required
def user():
    return render_template("user.html.j2", info=[{
        'type': 'user',
        'name': session['twitter_screen_name'],
        'text': login.verify_credentials()
    }])


@app.errorhandler(404)
def error404(e):
    return render_template('errors.html.j2', error=e), 404
