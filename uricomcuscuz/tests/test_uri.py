from itertools import zip_longest
from unittest.mock import patch

import pytest

from uricomcuscuz.ext.uri import (fetch_students, fetch_submissions,
                                  fetch_categories, profile_url, problem_url,
                                  university_pages)


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


def fetch_all__university(urls):
    """Faz de conta que estamos buscando as páginas da universidade
       e retornamos o html delas.
    """
    with open('uricomcuscuz/tests/fixtures/html/university.html', 'r') as f:
        yield f.read()


def fetch_all__profile(ids):
    """Faz de conta que estamos buscando as páginas do perfil de usuários
       e retornamos o html delas.
    """
    with open('uricomcuscuz/tests/fixtures/html/profile.html', 'r') as f:
        yield f.read()


def fetch_all__problem(ids):
    """Faz de conta que estamos buscando as páginas de problemas e
       retornamos o html delas.
    """
    with open('uricomcuscuz/tests/fixtures/html/problem.html', 'r') as f:
        yield f.read()


@patch('uricomcuscuz.ext.uri.fetch_all', fetch_all__university)
def test_fetch_students():
    """Testa a função para obter os estudantes na página da universidade."""
    students = list(fetch_students(total_pages=1))
    assert students == [('796', 'Anderson Lima'),
                        ('798', 'Thiago J. Barbalho'),
                        ('786', 'Marcos Daniel'),
                        ('11425', 'Claudivan Barreto')]


@patch('uricomcuscuz.ext.uri.fetch_all', fetch_all__profile)
def test_fetch_submissions():
    """Testa a função para obter as submissões na página do estudante."""
    # problem_id, problem_name, ranking, submission_id, lang, exec_time, date
    subs = [
        ('1001', 'Extremamente Basico', '04707º', '5795908', 'Python', '0.012',
        '05/12/2016 11:09:40'),
        ('1002', 'Area do Circulo', '21208º', '5796759', 'Python', '0.028',
        '05/12/2016 12:47:29'),
        ('1003', 'Soma Simples', '01272º', '5818546', 'Python', '0.008',
        '08/12/2016 17:14:53'),
    ]
    for submissions in fetch_submissions(user_ids=[1]):
        assert list(submissions) == subs


@patch('uricomcuscuz.ext.uri.fetch_all', fetch_all__problem)
def test_fetch_categories():
    """Testa a função para obter as categorias dos problemas."""
    categories = list(fetch_categories(problem_ids=[1]))
    assert categories == ['iniciante']
