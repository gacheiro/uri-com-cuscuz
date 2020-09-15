import pytest
from uricomcuscuz.models import User, Problem


@pytest.mark.parametrize(('Model', 'id', 'expected_link'), (
    (User, 1, '/judge/pt/profile/1?sort=Ranks.created&direction=desc'),
    (Problem, 1, '/judge/pt/problems/view/1'),
))
def test_link(populate_db, Model, id, expected_link):
    """Testa se os links para o URI estão corretos."""
    obj = Model.query.get(id)
    assert obj.link.endswith(expected_link)
