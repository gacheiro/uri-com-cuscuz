from itertools import zip_longest
import pytest

from uricomcuscuz.ext.uri import profile_url, problem_url, university_pages


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
