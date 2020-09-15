import pytest


def test_index(client, populate_db):
    rv = client.get('/')
    assert 200 == rv.status_code
    assert 3 == rv.data.count(b'Mr. Foo Bar')
    assert 2 == rv.data.count(b'Extremely easy problem')
    assert 1 == rv.data.count(b'Not so easy problem')
    assert b'iniciante' in rv.data
    assert b'grafos' in rv.data


def test_users(client, populate_db):
    rv = client.get('/users/1')
    assert 200 == rv.status_code
    assert 2 == rv.data.count(b'Extremely easy problem')
    assert 1 == rv.data.count(b'Not so easy problem')
    assert b'iniciante' in rv.data
    assert b'grafos' in rv.data


@pytest.mark.parametrize(('page', 'name', 'count'), (
    ('/problems/1', b'Mr. Foo Bar', 2),
    ('/problems/2', b'Mr. Foo Bar', 1),
))
def test_problems(client, populate_db, page, name, count):
    rv = client.get(page)
    assert 200 == rv.status_code
    assert rv.data.count(name) == count
