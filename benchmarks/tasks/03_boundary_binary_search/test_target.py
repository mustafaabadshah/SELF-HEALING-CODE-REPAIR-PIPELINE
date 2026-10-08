import pytest
from search import binary_search


def test_boundary_last_element():
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 9) == 4
    assert binary_search([42], 42) == 0
