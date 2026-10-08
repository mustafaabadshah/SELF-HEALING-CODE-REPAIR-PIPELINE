import pytest
from paginator import paginate_items


def test_exact_page_boundary_has_no_next():
    items = list(range(20))
    res = paginate_items(items, page=2, page_size=10)
    assert res["items"] == list(range(10, 20))
    assert res["has_next"] is False
