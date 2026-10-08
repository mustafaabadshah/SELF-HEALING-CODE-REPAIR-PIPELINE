import pytest
from paginator import paginate_items


def test_first_page_with_more_items():
    items = list(range(25))
    res = paginate_items(items, page=1, page_size=10)
    assert len(res["items"]) == 10
    assert res["has_next"] is True


def test_empty_items():
    res = paginate_items([], page=1, page_size=10)
    assert res["items"] == []
    assert res["has_next"] is False
