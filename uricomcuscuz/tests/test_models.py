import pytest
from uricomcuscuz.models import User, Problem, Submission


@pytest.mark.parametrize(('Model', 'id', 'expected_link'), (
    (User, 1, '/judge/pt/profile/1?sort=Ranks.created&direction=desc'),
    (Problem, 1, '/judge/pt/problems/view/1'),
))
def test_link(populate_db, Model, id, expected_link):
    """Testa se os links para o URI estão corretos."""
    obj = Model.query.get(id)
    assert obj.link.endswith(expected_link)


@pytest.mark.parametrize(('category', 'sub_ids'), (
    ('', [1, 2, 3]),
    ('iniciante', [1, 3]),
    ('grafos', [2]),
    ('geometria', []),
))
def test_query_by(populate_db, category, sub_ids):
    """Testa os filtros de submissões por categorias."""
    ids = [sub.id for sub in Submission.query_by(category=category).all()]
    assert ids == sub_ids
