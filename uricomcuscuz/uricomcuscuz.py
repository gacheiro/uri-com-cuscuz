import os
import datetime

from flask import Flask, render_template, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
import asyncio

from uricomcuscuz.scraping import (profile_url_sorted, problem_url, 
    fetch_all, parse_date)

app = Flask(__name__) 

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from .models import User, Submission, Problem


@app.route('/')
@app.route('/index')
def index(page=1):
    page = request.args.get('page', 1, type=int)
    submissions = (
        Submission
        .query
        .order_by(Submission.date.desc())
        .paginate(page, app.config['SUBS_PER_PAGE'], error_out=False)
    )
    g.endpoint = 'index'    # usado nos links da paginação
    return render_template(
        'index.html', 
        table_desc='Soluções mais recentes',
        thead=('Nome', 'Problema', 'Linguagem', 'Data'),
        pagination=submissions,
    )


@app.route('/user/<id>')
def user_page(id):
    page = request.args.get('page', 1, type=int)
    user = User.query.get_or_404(id)
    submissions = (
        Submission
        .query
        .filter_by(user_id=id)
        .order_by(Submission.date.desc())
        .paginate(page, app.config['SUBS_PER_PAGE'], error_out=False)
    )
    g.endpoint, g.id = 'user_page', id # usado nos links da paginação
    return render_template(
        'user.html', 
        table_desc=f'Ultimas soluções de {user.name}',
        external_link=profile_url_sorted(user.id),
        thead=('Nome', 'Tempo', 'Linguagem', 'Data'),
        pagination=submissions
    )


@app.route('/problem/<id>')
def problem_page(id):
    page = request.args.get('page', 1, type=int)
    problem = Problem.query.get_or_404(id)
    submissions = (
        Submission
        .query
        .filter_by(problem_id=id)
        .order_by(Submission.date.desc())
        .paginate(page, app.config['SUBS_PER_PAGE'], error_out=False)
    )
    g.endpoint, g.id = 'problem_page', id # usado nos links da paginação
    return render_template(
        'problem.html', 
        table_desc=f'Ultimas soluções para {problem.name}',
        external_link=problem_url(problem.id),
        thead=('Usuário', 'Tempo', 'Linguagem', 'Data'),
        pagination=submissions
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


@app.cli.command('fetch-subs')
def fetch_submissions():
    """Faz a raspagem de dados no site do URI e atualiza o bd."""
    print('Updating solutions...')
    total_pages = int(app.config['TOTAL_PAGES'])
    users, user_submissions = asyncio.run(fetch_all(total_pages))
    for (user_id, user_name), submissions in zip(users, user_submissions):
        user = User(id=user_id, name=user_name)
        db.session.merge(user)
        for sub in submissions:
            (problem_id, 
            problem_name, 
            ranking, 
            submission_id,
            language, 
            exec_time, 
            date) = sub
            problem = Problem(id=problem_id, name=problem_name)
            submission = Submission(id=submission_id,
                                    user_id=user_id,
                                    problem_id=problem_id,
                                    language=language,
                                    ranking=ranking[:-1], # remove o º do final
                                    exec_time=exec_time,
                                    date=parse_date(date))
            db.session.merge(problem)
            db.session.merge(submission)            
    db.session.commit()
    print('done.')
