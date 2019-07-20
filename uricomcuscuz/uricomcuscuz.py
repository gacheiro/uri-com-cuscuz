import os
import datetime

from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

from .scraping import profile_url_sorted, problem_url

app = Flask(__name__) 

app.config.from_object(os.environ['APP_SETTINGS'])
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
    return render_template(
        'index.html', 
        table_desc='Soluções mais recentes',
        thead=('Nome', 'Problema', 'Posição', 'Linguagem', 'Data'),
        tbody=submissions,
    )


@app.route('/user/<id>')
def user_page(id):
    user = User.query.get_or_404(id)
    uri_profile_link = profile_url_sorted(user.id)
    return render_template(
        'user.html', 
        table_desc=f'Ultimas soluções de {user.name}',
        external_link=uri_profile_link,
        thead=('Nome', 'Posição', 'Tempo', 'Linguagem', 'Data'),
        tbody=user.submissions
    )


@app.route('/problem/<id>')
def problem_page(id):
    problem = Problem.query.get_or_404(id)
    uri_profile_link = problem_url(problem.id)
    return render_template(
        'problem.html', 
        table_desc=f'Ultimas soluções para {problem.name}',
        external_link=uri_profile_link,
        thead=('Usuário', 'Posição', 'Tempo', 'Linguagem', 'Data'),
        tbody=problem.submissions
    )


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
