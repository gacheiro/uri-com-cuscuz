import asyncio
import os
import datetime

from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

     
app = Flask(__name__) 
app.config.from_object(__name__) # load config from this file

# Load default config and override config from an environment variable
app.config.update({
    'SECRET_KEY': 'this-really-needs-to-be-changed',
    'SQLALCHEMY_DATABASE_URI': os.environ['DATABASE_URL'],
})
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from .models import User, Submission, Problem


@app.route('/')
def index():
    submissions = (
        Submission
        .query
        .order_by(Submission.date.desc())
        .limit(100)
        .all()
    )
    return render_template('index.html', submissions=submissions)


@app.route('/user/<id>')
def user_page(id):
    user = User.query.get_or_404(id)
    return render_template('user.html', user=user)


@app.route('/problem/<id>')
def problem_page(id):
    problem = Problem.query.get_or_404(id)
    return render_template('problem.html', problem=problem)


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
