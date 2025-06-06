from backend.journeys_utils import get_default_journeys


def test_journeys_structure():
    journeys = get_default_journeys()
    assert len(journeys) >= 3
    for j in journeys:
        assert "id" in j
        assert "name" in j
        assert "description" in j
        assert isinstance(j.get("tasks"), list)
