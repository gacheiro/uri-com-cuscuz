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
