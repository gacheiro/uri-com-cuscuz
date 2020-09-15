import os
import datetime
import pytest

from uricomcuscuz import create_app
from uricomcuscuz.models import db, User, Problem, Submission

users = [
    {'id': 1, 'name': 'Mr. Foo Bar'},
]

problems = [
    {'id': 1, 'name': 'Extremely easy problem', 'category': 'iniciante'},
    {'id': 2, 'name': 'Not so easy problem', 'category': 'grafos'},
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


@pytest.fixture(scope='session')
def app():
    os.environ['APP_SETTINGS'] = 'config.TestingConfig'
    app = create_app()
    assert app.config['TESTING']
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def populate_db(client):
    db.session.bulk_insert_mappings(User, users)
    db.session.bulk_insert_mappings(Problem, problems)
    db.session.bulk_insert_mappings(Submission, submissions)
