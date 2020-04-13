import os
import datetime
import pytest

from uricomcuscuz import create_app
from uricomcuscuz.models import db, User, Problem, Submission

users = [
    {'name': 'Mr. Foo Bar'},
]

problems = [
    {'name': 'Extremely easy problem'},
    {'name': 'Not so easy problem'},
]

submissions = [
    {
        'user_id': 1,
        'problem_id': 1,
        'language': 'Python',
        'exec_time': 0.16,
        'ranking': 2,
        'date': datetime.datetime.now(),
    },
    {
        'user_id': 1,
        'problem_id': 2,
        'language': 'Python',
        'exec_time': 1.0,
        'ranking': 1,
        'date': datetime.datetime.now(),
    },
    {
        'user_id': 1,
        'problem_id': 1,
        'language': 'C++',
        'exec_time': 0.0,
        'ranking': 1,
        'date': datetime.datetime.now(),
    },
]


@pytest.fixture
def client():
    os.environ['APP_SETTINGS'] = 'config.TestingConfig'
    app = create_app()
    assert app.config['TESTING']
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def populate_db(client):
    for user in users:
        db.session.add(User(**user))
    for problem in problems:
        db.session.add(Problem(**problem))
    for sub in submissions:
        db.session.add(Submission(**sub))
    db.session.commit()
