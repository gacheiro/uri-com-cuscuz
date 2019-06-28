import asyncio
import os
import sqlite3
import datetime

from flask import Flask, render_template, jsonify
from werkzeug.contrib.cache import SimpleCache
from flask_sqlalchemy import SQLAlchemy


from .scraping import latest_solutions

     
app = Flask(__name__) 
app.config.from_object(__name__) # load config from this file

# Load default config and override config from an environment variable
app.config.update({
    'SECRET_KEY': 'this-really-needs-to-be-changed',
    'SQLALCHEMY_DATABASE_URI': os.environ['DATABASE_URL'],
})
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


cache = SimpleCache()
def get_latest_solutions():
    rv = cache.get('solutions')
    if rv is None:
        return []
    return rv


@app.route('/')
def show_entries():
    latest = get_latest_solutions()
    return render_template('show_solutions.html', entries=latest)


def same_day(datea, dateb):
    return (datea.day == dateb.day
            and datea.month == dateb.month
            and datea.year == dateb.year)


def month_name(month):
    return {
        1: 'Jan',
        2: 'Fev',
        3: 'Mar',
        4: 'Abr',
        5: 'Mai',
        6: 'Jun',
        7: 'Jul',
        8: 'Ago',
        9: 'Set',
        10: 'Out',
        11: 'Nov',
        12: 'Dez',
    }[month]


@app.context_processor
def utility_processor():

    def format_date(date, now=None):
        if now is None:
            now = datetime.datetime.now()

        if same_day(date, now):
            return f'{date.hour}:{date.minute:02d}'
        else:
            return f'{date.day} {month_name(date.month)}'

    return dict(format_date=format_date)
