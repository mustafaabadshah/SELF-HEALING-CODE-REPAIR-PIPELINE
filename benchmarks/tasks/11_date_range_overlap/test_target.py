import pytest
from intervals import is_overlapping


def test_touching_boundary_not_overlapping_when_exclusive():
    # [1, 5) and [5, 10) do not overlap when inclusive=False
    assert is_overlapping(1, 5, 5, 10, inclusive=False) is False
