import os
import datetime
import pytest

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
    os.environ['FLASK_ENV'] = 'test'
    from uricomcuscuz import app
    from uricomcuscuz.models import db
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def populate_db(client):
    from uricomcuscuz.models import db, User, Problem, Submission
    for user in users:
        db.session.add(User(**user))
    for problem in problems:
        db.session.add(Problem(**problem))
    for sub in submissions:
        db.session.add(Submission(**sub))
    db.session.commit()


def test_index(client, populate_db):
    rv = client.get('/')
    assert 200 == rv.status_code
    assert 3 == rv.data.count(b'Mr. Foo Bar')
    assert 2 == rv.data.count(b'Extremely easy problem')
    assert 1 == rv.data.count(b'Not so easy problem')


def test_users(client, populate_db):
    rv = client.get('/users/1')
    assert 200 == rv.status_code
    assert 2 == rv.data.count(b'Extremely easy problem')
    assert 1 == rv.data.count(b'Not so easy problem')


def test_problems(client, populate_db):
    rv = client.get('/problems/1')
    assert 200 == rv.status_code
    assert 2 == rv.data.count(b'Mr. Foo Bar')
    rv = client.get('/problems/2')
    assert 200 == rv.status_code
    assert 1 == rv.data.count(b'Mr. Foo Bar')
