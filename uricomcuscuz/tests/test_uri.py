from itertools import zip_longest
from unittest.mock import patch

import pytest

from uricomcuscuz.ext.uri import (fetch_students, fetch_submissions,
                                  fetch_problems, profile_url, problem_url,
                                  university_pages, stats)


@pytest.mark.parametrize(('id', 'url'), (
    (1, '/judge/pt/profile/1?sort=Ranks.created&direction=desc'),
    ('2', '/judge/pt/profile/2?sort=Ranks.created&direction=desc'),
))
def test_profile_url(id, url):
    assert profile_url(id).endswith(url)


@pytest.mark.parametrize(('id', 'url'), (
    (1, '/judge/pt/problems/view/1'),
    ('2', '/judge/pt/problems/view/2'),
))
def test_problem_url(id, url):
    assert problem_url(id).endswith(url)


@pytest.mark.parametrize(('total_pages', 'pages'), (
    (1, ['?page=1',]),
    (2, ['?page=1', '?page=2']),
))
def test_university_pages(total_pages, pages):
    urls = university_pages(total_pages)
    for url, page in zip_longest(urls, pages):
        assert url.endswith(page)


def fetch_all(paths=[]):
    """"Faz de conta que buscamos diversas páginas na web e retornamos o html
        delas. Só que estamos pegando as páginas do disco.

        Usamos junto com método patch para 'mockar' as chamadas http para o URI.
    """
    def fetch(urls):
        for path in paths:
            with open(path, 'r') as f:
                yield f.read()

    return fetch


def test_fetch_students():
    """Testa a função para obter os estudantes na página da universidade."""
    paths = ['uricomcuscuz/tests/fixtures/html/university.html']
    with patch('uricomcuscuz.ext.uri.fetch_all', fetch_all(paths)):
        students = list(fetch_students(total_pages=1))
        assert students == [('796', 'Anderson Lima'),
                            ('798', 'Thiago J. Barbalho'),
                            ('786', 'Marcos Daniel'),
                            ('11425', 'Claudivan Barreto')]


def test_fetch_submissions():
    """Testa a função para obter as submissões na página do estudante."""
    paths = ['uricomcuscuz/tests/fixtures/html/profile.html']
    # problem_id, problem_name, ranking, submission_id, lang, exec_time, date
    subs = [
        ('1001', 'Extremamente Basico', '04707º', '5795908', 'Python', '0.012',
        '05/12/2016 11:09:40'),
        ('1002', 'Area do Circulo', '21208º', '5796759', 'Python', '0.028',
        '05/12/2016 12:47:29'),
        ('1003', 'Soma Simples', '01272º', '5818546', 'Python', '0.008',
        '08/12/2016 17:14:53'),
    ]
    with patch('uricomcuscuz.ext.uri.fetch_all', fetch_all(paths)):
        for submissions in fetch_submissions(user_ids=[1]):
            assert list(submissions) == subs


def test_fetch_problems():
    """Testa a função para obter as categorias dos problemas."""
    paths = ['uricomcuscuz/tests/fixtures/html/problem.html']
    with patch('uricomcuscuz.ext.uri.fetch_all', fetch_all(paths)):
        problems = list(fetch_problems(problem_ids=[1]))
        assert problems == [('Extremamente Basico', 'iniciante')]


def todo_test_cli__update():
    """Testa o commando `flask uri update`."""
    # TODO
    ...


def test_cli__stats(app, populate_db):
    """Testa o comando `flask uri stats`."""
    runner = app.test_cli_runner()
    result = runner.invoke(stats)

    assert result.exit_code == 0
    assert 'number of users: 1' in result.output
    assert 'number of submissions: 3' in result.output
    assert 'number of problems solved: 2' in result.output
    assert 'number of distinct languages: 2' in result.output
