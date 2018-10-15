from webapp import app
from aggregator import Twit, User
from flask import session, request, url_for, render_template

@app.route('/')
def index():
    return render_template("index.html")
