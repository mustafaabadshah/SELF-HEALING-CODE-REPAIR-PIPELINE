import pytest
from intervals import is_overlapping


def test_clear_overlap():
    assert is_overlapping(1, 10, 5, 15, inclusive=False) is True
    assert is_overlapping(1, 10, 5, 15, inclusive=True) is True


def test_clear_disjoint():
    assert is_overlapping(1, 4, 6, 10, inclusive=False) is False


def test_touching_when_inclusive():
    assert is_overlapping(1, 5, 5, 10, inclusive=True) is True
