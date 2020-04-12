import asyncio

from flask import current_app

from uricomcuscuz.ext.uri import fetch_all, parse_date
from uricomcuscuz.models import db, User, Problem, Submission


def create_db():
    """Cria as tabelas no bd."""
    db.create_all()


def drop_db():
    """Deleta as tabelas no db."""
    db.drop_all()


def fetch_submissions():
    """Faz a raspagem de dados no site do URI e atualiza o bd."""
    print('Updating solutions...')
    total_pages = int(current_app.config['TOTAL_PAGES'])
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


def init_app(app):
    """Registra os comandos no app."""
    for command in [create_db, drop_db, fetch_submissions]:
        app.cli.add_command(app.cli.command('fetch-subs')(command))
