from webapp import app
from aggregator import Twit, User
from flask import session, request, url_for, render_template

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template("index.html")

@app.errorhandler(404)
def error404(e):
    return render_template("404.html"), 404
