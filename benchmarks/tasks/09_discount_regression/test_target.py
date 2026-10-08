import pytest
from pricing import apply_discount


def test_percentage_string():
    assert apply_discount(200.0, "15%") == 170.0
