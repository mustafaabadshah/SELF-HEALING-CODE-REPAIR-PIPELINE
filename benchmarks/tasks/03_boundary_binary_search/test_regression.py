import pytest
from search import binary_search


def test_middle_elements():
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 3) == 1
    assert binary_search(arr, 5) == 2


def test_element_not_found():
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 6) is None
    assert binary_search([], 1) is None
